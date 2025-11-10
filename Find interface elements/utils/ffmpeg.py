import subprocess
from pathlib import Path
import os

video_list = ["2025-09-17_17-13-08.mp4",
              "2025-09-17_17-18-32.mp4",
              "2025-09-29_12-07-51.mp4",
              "mining_asteroid_01_60_fps.mp4",
              "mining_asteroid_02.mp4",
              "mining_asteroid_03.mp4",
              "mining_asteroid_04.mp4"]

BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)
os.chdir("../data")

input = r"video"
output = r"shared"

for video in video_list:
    video_name = Path(video).stem
    fullcommand = ["ffmpeg", "-i", f"{input}/{video}", "-vf",
                   "select='gt(scene,0.02)',showinfo", "-fps_mode", "vfr", "-frame_pts", "1",
                   f"{output}/{video_name}/images/{video_name}_%010d.jpg"]
    os.makedirs(f"{output}/{video_name}/images", exist_ok=True)

    try:
        result = subprocess.run(fullcommand, capture_output=True, text=True, check=True)
    except Exception as e:
        print("RETURNCODE:", result.returncode)
        print("STDOUT:\n", result.stdout)
        print("STDERR:\n", result.stderr)
