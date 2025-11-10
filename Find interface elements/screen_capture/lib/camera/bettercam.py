from threading import Event, Lock
import bettercam
import win32gui
import win32api
import time


class WindowsCapture():

    def __init__(self, window_title):
        self.TARGET_FPS = 30
        self.CAPTURE_WINDOW_TITLE = window_title
        self.VIDEO_OUTPUT_WIDTH = 1280
        self.VIDEO_OUTPUT_HEIGHT = 720

    camera = None
    HWND = None
    
    def start_capture(self):
        
        self.HWND = self._find_hwnd_by_title_sub(self.CAPTURE_WINDOW_TITLE)

        def create_camera():
            self.camera = self._create_bettercam_for_window(self.HWND)
            self.camera.start(target_fps=self.TARGET_FPS, video_mode=False)

        create_camera()

    def stop_capture(self):
        if self.camera:
            self.camera.stop()

    def get_latest_frame(self):
        return self.camera.get_latest_frame()

    # def regrab_region(self):
    #     _, _, region_local = self._get_region_local(self.HWND)
    #     self.camera.grab(region=region_local)

    def _get_region_local(self, hwnd):
        
        # получаем window rect (виртуальные coords)
        left, top, right, bottom = self._get_window_rect(hwnd)
        w = right - left
        h = bottom - top
        # найдём монитор, на которой расположено окно
        mon_idx, mon = self._find_monitor_for_rect((left, top, right, bottom))
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

        region_local = (int(local_left), int(local_top), int(local_left)+int(w), int(local_top)+int(h))

        return mon_idx, mon, region_local
        

    def _find_hwnd_by_title_sub(self, sub):
        hwnds = []
        def enum_cb(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and sub.lower() in title.lower():
                    hwnds.append(hwnd)
        win32gui.EnumWindows(enum_cb, None)
        return hwnds[0] if hwnds else None

    def _get_window_rect(self, hwnd):
        # Возвращает (left, top, right, bottom) в виртуальных экранных координатах
        return win32gui.GetWindowRect(hwnd)
    
    # --- Заменить эту функцию вместо предыдущей _enum_monitors() ---
    def _enum_monitors(self):
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

    def _find_monitor_for_rect(self, rect):
        """rect = (left, top, right, bottom) виртуальные coords -> возвращаем (index, monitor)"""
        monitors = self._enum_monitors()
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
    
    def _create_bettercam_for_window(self, hwnd):
        
        device_idx, mon, region_local = self._get_region_local(hwnd)
        #print("Window rect (virtual):", (left, top, right, bottom))
        print("Monitor index:", device_idx, "monitor_rect:", (mon['left'], mon['top'], mon['right'], mon['bottom']))
        print("Using region_local (on monitor):", region_local, "device_idx:", device_idx)

        # попробуем создать bettercam с region (и попросим RGB)
        cam = bettercam.create(device_idx=device_idx, region=region_local, output_color="BGR")
        return cam
