# minimal_win_capture_pyglet.py
# Requires: pip install windows-capture pyglet
import threading
import pyglet
import time

# Попытка импортировать windows-capture (если нет — подсказка)
try:
    from windows_capture import WindowsCapture
except Exception as e:
    raise SystemExit("Install windows-capture (pip install windows-capture) and run from regular Python (not notebook).") from e

# Параметры окна
W = 1280
H = 720
TITLE = "minimal windows-capture -> pyglet"

# Global для последнего сыро/байтового кадра
latest = None      # будет (bytes, width, height, channels)
lock = threading.Lock()
stop_event = threading.Event()

# Очень простой обработчик: берем raw-буфер и метаданные кадра и сохраняем в latest.
def attach_capture_handlers(capture):
    @capture.event
    def on_frame_arrived(frame, _capture_control):
        # Попытаемся получить байты и размеры — предполагаем, что frame.buffer() и frame.width/height существуют.
        try:
            buf = frame.buffer() if callable(getattr(frame, "buffer", None)) else getattr(frame, "buffer", None)
            # buf может быть bytes, bytearray или memoryview
            raw = bytes(buf)
        except Exception:
            # Если не удалось — пропускаем кадр
            return

        # width/height — могут быть атрибутами или методами
        try:
            w = frame.width() if callable(getattr(frame, "width", None)) else getattr(frame, "width", None)
            h = frame.height() if callable(getattr(frame, "height", None)) else getattr(frame, "height", None)
        except Exception:
            return

        if not (isinstance(w, int) and isinstance(h, int)):
            return

        # простая оценка числа каналов по длине буфера
        chans = None
        L = len(raw)
        if L == w * h * 4:
            chans = 4
        elif L == w * h * 3:
            chans = 3
        else:
            # если не совпадает — попробуем делить
            if (w * h) > 0 and (L % (w*h)) == 0:
                chans = L // (w*h)
            else:
                # неизвестный формат — пропускаем
                return

        with lock:
            # сохраняем как сырые байты — без преобразования
            latest = (raw, int(w), int(h), int(chans))
            # помним в глобал для pyglet
            globals()['latest'] = latest

    @capture.event
    def on_closed():
        stop_event.set()

# Pyglet окно — рендерит последний байтовый кадр «как есть»
def run_pyglet():
    window = pyglet.window.Window(W, H, caption=TITLE, resizable=True)

    @window.event
    def on_draw():
        window.clear()
        with lock:
            cur = globals().get('latest', None)
        if not cur:
            pyglet.text.Label("Waiting for frames...\nPress ESC to quit", x=10, y=window.height-20).draw()
            return

        raw, w, h, chans = cur
        fmt = 'RGB' if chans == 3 else 'RGBA'  # прямо используем входной layout
        # создаём ImageData из байтов (никаких конверсий)
        img = pyglet.image.ImageData(w, h, fmt, raw, pitch=-w * chans)
        img.blit(0, 0, width=window.width, height=window.height)

    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            stop_event.set()
            window.close()

    pyglet.app.run()

def main():
    # Создаём capture (picker/dialog по-умолчанию)
    cap = WindowsCapture(window_name="Visual Studio Code", monitor_index=None)
    attach_capture_handlers(cap)
    cap.start()          # запускает внутренние потоки/захват
    try:
        run_pyglet()     # главный поток рисует
    finally:
        try:
            cap.stop()
        except Exception:
            pass
        stop_event.set()

if __name__ == "__main__":
    main()
