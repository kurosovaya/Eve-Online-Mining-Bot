from lib.camera.bettercam import WindowsCapture
import pyglet
from threading import Event, Lock, Thread
import time
from ultralytics.models import YOLO
import queue
import numpy as np


latest_vis = None
INFER_FPS = 30
stop_event = Event()
frame_lock = Lock()
infer_q = queue.Queue(maxsize=1)
capture = WindowsCapture("EVE Launc")
window = pyglet.window.Window(width=capture.VIDEO_OUTPUT_WIDTH,
                                height=capture.VIDEO_OUTPUT_HEIGHT,
                                caption="Output", resizable=True)
fps_display = pyglet.window.FPSDisplay(window)
model = YOLO(r"D:\\Projects\\my_ml_backend\\models\\RectangleLabelsObbModel\\weights\\best.pt")
img = None
_buf = None
_buf_np = None
CONF = 0.25
IMGSZ = 960


@window.event
def on_draw():
    global img, _buf, _buf_np
    window.clear()
    with frame_lock:
        frame = None if latest_vis is None else latest_vis
    if frame is None:
        pyglet.text.Label("No frames yet...", x=10, y=window.height-20).draw()
        return
    h, w = frame.shape[:2]
    if not frame.flags["C_CONTIGUOUS"]:
        frame = np.ascontiguousarray(frame)
    if img is None:        
        _buf = bytearray(w * h * 3)
        _buf_np = np.frombuffer(_buf, dtype=np.uint8)
        _buf_np[:] = frame.reshape(-1)
        img = pyglet.image.ImageData(w, h, 'BGR', _buf, pitch=-w*3)
    else:
        _buf_np[:] = frame.reshape(-1)
        img.set_data('BGR', -w * 3, _buf) 
    img.blit(0, 0, width=window.width, height=window.height)
    fps_display.draw()

def screen_capture():

    while not stop_event.is_set():
        frame = capture.get_latest_frame()
        if frame is None:
            time.sleep(0.001)
            continue

        try:
            infer_q.get_nowait()
        except queue.Empty:
            pass
        try:
            infer_q.put_nowait(frame)
        except queue.Full:
            pass

def inference_thread_func():
    global latest_vis
    while True:
        frame_bgr = infer_q.get()
        if frame_bgr is None:
            continue

        infer_period = 1.0 / INFER_FPS
        last = 0.0

        now = time.perf_counter()
        if now - last < infer_period:
            continue
        last = now

        results = model.predict(
            source=frame_bgr, imgsz=IMGSZ, conf=CONF,
            save=False, stream=False, verbose=False, device="cpu"
        )
        res = results[0]
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
