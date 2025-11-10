from windows_capture import WindowsCapture, Frame, InternalCaptureControl
import time

avg_frames = []
all_frames = []

for i in range(10):
    DUR = 5.0
    count = 0
    start_ts = None

    # Any error from on_closed and on_frame_arrived will surface here
    capture = WindowsCapture(
        cursor_capture=None,
        draw_border=None,
        monitor_index=None,
        window_name=None,
    )


    # Called every time a new frame is available
    @capture.event
    def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
        

        # Save the frame as an image to the specified path
        global count, start_ts
        if start_ts is None:
            print("New frame arrived")
            start_ts = time.time()
        count += 1
        if time.time() - start_ts > DUR:
            capture_control.stop()
        # Gracefully stop the capture thread



    # Called when the capture item closes (usually when the window closes).
    # The capture session will end after this function returns.
    @capture.event
    def on_closed():
        print("Capture session closed")


    capture.start()
    elapsed = time.time() - (start_ts or time.time())
    print("windows-capture: frames:", count, "elapsed:", round(elapsed,3),
           "fps:", round(count / max(elapsed, 1e-6), 2))
    avg_frames.append(round(count / max(elapsed, 1e-6)))
    all_frames.append(count)

print("windows-capture: frames:", (sum(all_frames)/10), 
       "fps:", sum(avg_frames)/10)