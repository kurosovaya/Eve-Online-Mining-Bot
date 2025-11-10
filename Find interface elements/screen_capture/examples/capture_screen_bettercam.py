# bettercam_to_pyglet_window_region.py
import threading
import time
import ctypes
import bettercam
import numpy as np
import pyglet
import win32gui
import win32api

TARGET_FPS = 60
WINDOW_TITLE = "bettercam -> pyglet (fixed)"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Под строкой ищем окно (регистронезависимо)
CAPTURE_WINDOW_TITLE_SUB = "windows_capture"  # <-- измени сюда

latest_frame = None
frame_lock = threading.Lock()
stop_event = threading.Event()
_debug_printed = False

def find_hwnd_by_title_sub(sub):
    hwnds = []
    def enum_cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title and sub.lower() in title.lower():
                hwnds.append(hwnd)
    win32gui.EnumWindows(enum_cb, None)
    return hwnds[0] if hwnds else None

def get_window_rect(hwnd):
    # Возвращает (left, top, right, bottom) в виртуальных экранных координатах
    return win32gui.GetWindowRect(hwnd)

# --- Заменить эту функцию вместо предыдущей enum_monitors() ---
def enum_monitors():
    """
    Возвращает список мониторов в формате:
    [{'left','top','right','bottom','width','height','hmonitor'}, ...]
    Работает с разными версиями pywin32 (EnumDisplayMonitors может возвращать список).
    """
    monitors = []
    try:
        # win32api.EnumDisplayMonitors возвращает list of tuples: (hMonitor, hdcMonitor, (left,top,right,bottom))
        mons = win32api.EnumDisplayMonitors(None, None)
        for item in mons:
            # item обычно (hMonitor, hdcMonitor, rect)
            hMonitor = item[0]
            # Получим полную информацию через GetMonitorInfo
            try:
                mi = win32api.GetMonitorInfo(hMonitor)
                r = mi.get('Monitor') or mi.get('Work') or mi.get('MonitorRect')
                # r может быть tuple(left, top, right, bottom)
                left, top, right, bottom = r
            except Exception:
                # последний ресурс — если прямоугольник уже в item[2]
                rect = item[2]
                left, top, right, bottom = rect

            monitors.append({
                'left': left, 'top': top, 'right': right, 'bottom': bottom,
                'width': right - left, 'height': bottom - top,
                'hmonitor': hMonitor
            })
        return monitors
    except TypeError:
        # на всякий случай — пробуем более простой путь: получить primary monitor через GetMonitorInfo(0)
        try:
            hmon = win32api.MonitorFromPoint((0,0))
            mi = win32api.GetMonitorInfo(hmon)
            r = mi.get('Monitor') or mi.get('Work')
            left, top, right, bottom = r
            return [{
                'left': left, 'top': top, 'right': right, 'bottom': bottom,
                'width': right-left, 'height': bottom-top,
                'hmonitor': hmon
            }]
        except Exception:
            # окончательный fallback: одна запись для 0..screen
            wx = win32api.GetSystemMetrics(0)
            hy = win32api.GetSystemMetrics(1)
            return [{
                'left': 0, 'top': 0, 'right': wx, 'bottom': hy,
                'width': wx, 'height': hy, 'hmonitor': None
            }]

def find_monitor_for_rect(rect):
    """rect = (left, top, right, bottom) виртуальные coords -> возвращаем (index, monitor)"""
    monitors = enum_monitors()
    l, t, r, b = rect
    # pick monitor with the largest intersection area
    best_idx = None
    best_area = 0
    for i, m in enumerate(monitors):
        ix = max(0, min(r, m['right']) - max(l, m['left']))
        iy = max(0, min(b, m['bottom']) - max(t, m['top']))
        area = ix * iy
        if area > best_area:
            best_area = area
            best_idx = i
    if best_idx is None:
        return None, None
    return best_idx, monitors[best_idx]

def create_bettercam_for_window(hwnd):
    # получаем window rect (виртуальные coords)
    left, top, right, bottom = get_window_rect(hwnd)
    w = right - left
    h = bottom - top
    # найдём монитор, на которой расположено окно
    mon_idx, mon = find_monitor_for_rect((left, top, right, bottom))
    if mon is None:
        raise RuntimeError("Не удалось найти монитор для окна")

    # локальные координаты в пространстве монитора
    local_left = left - mon['left']
    local_top = top - mon['top']

    # убедимся что регион внутри монитора (обрежем если пересекает границу)
    local_left = max(0, local_left)
    local_top = max(0, local_top)
    if local_left + w > mon['width']:
        w = max(0, mon['width'] - local_left)
    if local_top + h > mon['height']:
        h = max(0, mon['height'] - local_top)

    region_local = (int(local_left), int(local_top), int(w), int(h))
    device_idx = mon_idx  # bettercam device index соответствует порядку мониторов в EnumDisplayMonitors

    print("Window rect (virtual):", (left, top, right, bottom))
    print("Monitor index:", device_idx, "monitor_rect:", (mon['left'], mon['top'], mon['right'], mon['bottom']))
    print("Using region_local (on monitor):", region_local, "device_idx:", device_idx)

    # попробуем создать bettercam с region (и попросим RGB)
    try:
        cam = bettercam.create(device_idx=device_idx, region=region_local, output_color="RGB")
    except TypeError:
        # разные версии bettercam могут принимать параметры по-разному — пробуем варианты
        try:
            cam = bettercam.create(region=region_local, output_color="RGB")
        except Exception as e:
            print("bettercam.create failed:", e)
            raise
    return cam

def ensure_rgb_frame(frame):
    if frame is None:
        return None
    if not isinstance(frame, np.ndarray) or frame.ndim != 3:
        return None
    ch = frame.shape[2]
    if ch == 4:
        bgr = frame[..., :3].astype(np.float32)
        a = frame[..., 3].astype(np.float32) / 255.0
        a = np.clip(a, 1e-6, 1.0)[..., None]
        bgr = (bgr / a).clip(0, 255).astype(np.uint8)
        arr = bgr
    else:
        arr = frame
    # если arr по-прежнему BGR (эвристика)
    b_mean = float(arr[..., 0].mean())
    r_mean = float(arr[..., 2].mean())
    if (b_mean - r_mean) > 10:
        rgb = arr[..., ::-1]
    else:
        rgb = arr.copy()
    return np.ascontiguousarray(rgb)

def capture_thread_func():
    global latest_frame, _debug_printed
    hwnd = find_hwnd_by_title_sub(CAPTURE_WINDOW_TITLE_SUB)
    if not hwnd:
        raise RuntimeError(f"Окно с подстрокой '{CAPTURE_WINDOW_TITLE_SUB}' не найдено. Проверь заголовок и что окно не свернуто.")

    try:
        cam = create_bettercam_for_window(hwnd)
    except Exception as e:
        print("bettercam setup failed, falling back to mss. Error:", e)
        # fallback: use mss on full window rect (virtual coords)
        import mss
        sct = mss.mss()
        left, top, right, bottom = get_window_rect(hwnd)
        bbox = {"left": left, "top": top, "width": right - left, "height": bottom - top}
        print("Using mss bbox:", bbox)
        try:
            while not stop_event.is_set():
                s = sct.grab(bbox)
                arr = np.array(s)  # BGRA
                frame = arr[..., :3]  # BGR
                rgb = frame[..., ::-1]
                with frame_lock:
                    latest_frame = rgb
                time.sleep(1.0 / TARGET_FPS)
        finally:
            return

    # start cam (safe)
    try:
        cam.start(target_fps=TARGET_FPS)
    except TypeError:
        cam.start()

    try:
        while not stop_event.is_set():
            frame = cam.get_latest_frame()
            if frame is None:
                time.sleep(0.001)
                continue
            rgb = ensure_rgb_frame(frame)
            if rgb is None:
                continue
            with frame_lock:
                latest_frame = rgb
            if not _debug_printed:
                with frame_lock:
                    f = latest_frame
                if isinstance(f, np.ndarray) and f.ndim == 3 and f.shape[2] >= 3:
                    print("[bettercam debug] frame.shape:", f.shape, "dtype:", f.dtype)
                    print("[bettercam debug] channel means (R,G,B):",
                          float(f[...,0].mean()), float(f[...,1].mean()), float(f[...,2].mean()))
                _debug_printed = True
    finally:
        try:
            cam.stop()
        except Exception:
            pass

# pyglet window (ожидает RGB)
window = pyglet.window.Window(width=WINDOW_WIDTH, height=WINDOW_HEIGHT, caption=WINDOW_TITLE, resizable=True)

@window.event
def on_draw():
    window.clear()
    with frame_lock:
        frame = None if latest_frame is None else latest_frame.copy()
    if frame is None:
        pyglet.text.Label("No frames yet...", x=10, y=window.height-20).draw()
        return
    h, w = frame.shape[:2]
    data = frame.tobytes()
    img = pyglet.image.ImageData(w, h, 'RGB', data, pitch=-w*3)
    img.blit(0, 0, width=window.width, height=window.height)

def update(dt):
    window.dispatch_event('on_draw')

def _on_close_handler():
    stop_event.set()
    capture_thread.join(timeout=1.0)
    window.close()

window.push_handlers(on_close=_on_close_handler)

capture_thread = threading.Thread(target=capture_thread_func, daemon=True)
capture_thread.start()

pyglet.clock.schedule_interval(update, 1.0 / TARGET_FPS)

try:
    pyglet.app.run()
finally:
    stop_event.set()
    capture_thread.join(timeout=1.0)
