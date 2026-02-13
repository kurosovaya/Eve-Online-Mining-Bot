from windows_capture import WindowsCapture, Frame, InternalCaptureControl
import pyglet
from threading import Event, Lock, Thread
import time
from ultralytics.models import YOLO
import queue
import numpy as np
import cv2
from cv_eve.lib.other.snapshot import Snapshot, SharedState


latest_vis = None
INFER_FPS = 30
stop_event = Event()
frame_lock = Lock()
infer_q = queue.Queue(maxsize=1)
shared_state = SharedState()
capture = WindowsCapture(
    monitor_index=None,
    window_name="EVE - Kurosovaya I",
    cursor_capture=False,
    draw_border=False,
    minimum_update_interval=1000 // INFER_FPS
)
window = pyglet.window.Window(width=1280,
                              height=720,
                              caption="Output", resizable=False)
fps_display = pyglet.window.FPSDisplay(window)
model = YOLO(r"D:\Projects\my_ml_backend\models\runs\obb\runs\y11s_custom_1920\weights\best.pt")
img = None
_buf = None
_buf_np = None
CONF = 0.25
IMGSZ = 960


@capture.event
def on_frame_arrived(frame: Frame, control: InternalCaptureControl):
    global infer_q
    bgr = frame.convert_to_bgr().frame_buffer

    if bgr is None:
        time.sleep(0.001)
        return

    try:
        infer_q.get_nowait()
    except queue.Empty:
        pass
    try:
        bgr = np.ascontiguousarray(bgr).copy()
        infer_q.put_nowait(bgr)
    except queue.Full:
        pass

@capture.event
def on_closed():
    print("Capture closed")

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


def inference_thread_func():
    global latest_vis
    infer_period = 1.0 / INFER_FPS
    last = 0.0
    while True:
        frame_bgr = infer_q.get()
        if frame_bgr is None:
            continue

        now = time.perf_counter()
        if now - last < infer_period:
            continue
        last = now

        results = model.predict(
            source=frame_bgr, imgsz=IMGSZ, conf=CONF,
            save=False, stream=False, verbose=False, device="cpu"
        )
        res = results[0]
        polys = res.obb.xyxyxyxy
        confs = res.obb.conf
        clss  = res.obb.cls

        polys = polys.cpu().numpy().astype(np.int32)   # (N,4,2)
        confs = confs.cpu().numpy()
        clss  = clss.cpu().numpy().astype(int)
        shared_state.update(Snapshot())

        for poly, conf, cls_id in zip(polys, confs, clss):
            pts = poly.astype(np.int32).reshape(-1, 1, 2)  # (4,1,2)
            cv2.polylines(frame_bgr, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
            label = f"{res.names[int(cls_id)]} {conf:.2f}"
            x, y = pts[0, 0]
            cv2.putText(frame_bgr, label, (x, max(0, y - 5)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
            
        with frame_lock:
            latest_vis = frame_bgr



def update(dt):
    window.dispatch_event('on_draw')

def _on_close_handler():
    stop_event.set()
    window.close()


window.push_handlers(on_close=_on_close_handler)
inference_thread = Thread(target=inference_thread_func, daemon=True)
pyglet.clock.schedule_interval(update, 1.0 / INFER_FPS)

if __name__ == "__main__":
    try:
        capture.start_free_threaded()
        inference_thread.start()
        pyglet.app.run()
    finally:
        stop_event.set()
