from lib.camera.bettercam import WindowsCapture
import pyglet
from threading import Event, Lock, Thread
import time
from ultralytics.models import YOLO
from PIL import Image
from pathlib import Path
import queue


latest_frame = None
latest_vis = None
stop_event = Event()
frame_lock = Lock()
infer_q = queue.Queue(maxsize=1)
capture = WindowsCapture("EVE - 2x")
window = pyglet.window.Window(width=capture.VIDEO_OUTPUT_WIDTH,
                                height=capture.VIDEO_OUTPUT_HEIGHT,
                                caption="Output", resizable=True)
model = YOLO(r"Find interface elements/output_kaggle/results_v2/runs/y11s_custom/weights/best.pt")
CONF = 0.25
IMGSZ = 960


@window.event
def on_draw():
    window.clear()
    with frame_lock:
        frame = None if latest_vis is None else latest_vis.copy()
    if frame is None:
        pyglet.text.Label("No frames yet...", x=10, y=window.height-20).draw()
        return
    h, w = frame.shape[:2]
    data = frame.tobytes()
    img = pyglet.image.ImageData(w, h, 'BGR', data, pitch=-w*3)
    img.blit(0, 0, width=window.width, height=window.height)

def screen_capture():
    global latest_frame

    while not stop_event.is_set():
        frame = capture.get_latest_frame()
        if frame is None:
            time.sleep(0.001)
            continue
        with frame_lock:
            latest_frame = frame

def inference_thread_func():
    global latest_vis, latest_frame
    while True:
        with frame_lock:
            frame_bgr = latest_frame  # блокируемся, ждём новый кадр
        if frame_bgr is None:
            continue

        # Быстрый режим без лишнего вывода и без сохранений на диск
        results = model.predict(
            source=frame_bgr, imgsz=IMGSZ, conf=CONF,
            save=False, stream=False, verbose=False, device="cpu"  # или "cuda:0"
        )
        res = results[0]

        # Получаем аннотированную картинку (BGR) и конвертируем обратно в RGB для pyglet
        vis_bgr = res.plot()

        with frame_lock:
            latest_vis = vis_bgr

def update(dt):
    window.dispatch_event('on_draw')

def _on_close_handler():
    stop_event.set()
    capture_thread.join(timeout=1.0)
    window.close()


window.push_handlers(on_close=_on_close_handler)
capture_thread = Thread(target=screen_capture, daemon=True)
inference_thread = Thread(target=inference_thread_func, daemon=True)
pyglet.clock.schedule_interval(update, 1.0 / capture.TARGET_FPS)

if __name__ == "__main__":
    try:
        capture.start_capture()
        capture_thread.start()
        inference_thread.start()
        pyglet.app.run()
    finally:
        capture.stop_capture()
        stop_event.set()
        capture_thread.join(timeout=1.0)
