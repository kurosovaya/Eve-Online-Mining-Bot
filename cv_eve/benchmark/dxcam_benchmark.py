# bench_dxcam.py
import time
import dxcam

avg_frames = []
all_frames = []

for i in range(10):
    DUR = 5.0
    try:
        cam = dxcam.create(output_color="RGB")
    except TypeError:
        cam = dxcam.create()
    try:
        cam.start(target_fps=240)
    except TypeError:
        cam.start()
    t0 = time.time()
    frames = 0
    first_ts = None
    while time.time() - t0 < DUR:
        f = cam.get_latest_frame()
        if f is None:
            continue
        if first_ts is None:
            first_ts = time.time()
        frames += 1
    t = time.time() - t0
    try:
        cam.stop()
    except Exception:
        pass
    print("dxcam: frames:", frames, "elapsed:", round(t,3), "fps:", round(frames / t, 2))
    avg_frames.append(round(frames / t))
    all_frames.append(frames)

print("windows-capture: frames:", (sum(all_frames)/10), 
       "fps:", sum(avg_frames)/10)