from ultralytics.models import YOLO
import os
import json
import shutil
from pathlib import Path
import subprocess
from urllib.parse import urlparse, parse_qs
from collections import namedtuple


BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)

generated_paths = namedtuple("generated_paths", ["PROJECT_DIR", "ROOT_DIR", "ROOT_FOLDER_NAME",
                                                  "IMAGES_DIR", "PREVIEW_DIR", "INPUT_JSON",
                                                    "OUT_JSON"])

folders = [
    "2025-09-17_17-13-08",
    # "2025-09-17_17-18-32",
    # "2025-09-29_12-07-51",
    # "mining_asteroid_01_60_fps",
    # "mining_asteroid_02",
    # "mining_asteroid_03",
    # "mining_asteroid_04",
]

def generate_paths(folder_for_convertion, root_folder_name="pred2"):

    PROJECT_DIR = Path(f"EVE-images/{folder_for_convertion}")
    ROOT_DIR = PROJECT_DIR / root_folder_name
    IMAGES_DIR = Path(f"EVE-images/{folder_for_convertion}") / root_folder_name / "images"
    PREVIEW_DIR = ROOT_DIR / "preview"
    INPUT_JSON = ROOT_DIR / "output.json"
    OUT_JSON = ROOT_DIR / "output_with_preview.json"

    data_paths = generated_paths(PROJECT_DIR, ROOT_DIR, root_folder_name,
                                 IMAGES_DIR, PREVIEW_DIR, INPUT_JSON, OUT_JSON)
    return data_paths


def export_to_label_studio(data_paths: generated_paths, make_images_dir=False):

    files = sorted(data_paths.IMAGES_DIR.glob("*.jpg"))
    batch_size = 100
    model = YOLO(r"../output_kaggle/results_v2/runs/y11s_custom/weights/best.pt")

    for f in range(0, len(files), batch_size):
        results = model.predict(
            source=files[f:f+batch_size],
            imgsz=960,
            conf=0.10,
            save=True,
            save_txt=True,
            save_conf=True,
            stream=True,
            exist_ok=True,
            name=data_paths.ROOT_FOLDER_NAME,
            project=data_paths.PROJECT_DIR,
        )

        if make_images_dir:
            out_images_dir = data_paths.IMAGES_DIR
            os.makedirs(out_images_dir, exist_ok=True)
        for r in results:
            if make_images_dir:
                shutil.move(r.path, str(out_images_dir / Path(r.path).name))

        out_preview_dir = data_paths.PREVIEW_DIR
        os.makedirs(out_preview_dir, exist_ok=True)
        for img in data_paths.ROOT_DIR.glob("*.jpg"):
            shutil.move(img, out_preview_dir)

        class_file = data_paths.ROOT_DIR / "classes.txt"
        if not class_file.is_file():
            shutil.copy2("./classes.txt", str(class_file))


def label_studio_converter(data_paths: generated_paths):
    
    command = r".\convert_for_label_studio.ps1"
    convert_dir = ".\\" + str(data_paths.ROOT_DIR)
    out_json = ".\\" + str(data_paths.INPUT_JSON)
    image_root_url = f"/data/local-files/?d={str(data_paths.IMAGES_DIR)}"

    full_command = [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        command,
        "-DatasetRoot",
        convert_dir,
        "-OutJson",
        out_json,
        "-ImageRootUrl",
        image_root_url,
    ]
    result = subprocess.run(full_command, capture_output=True, text=True, check=True)
    print(result.returncode)
    print(result.stdout)
    print(result.stderr)


def merge_json(json1, json2):

    pass

def add_preview_to_json(data_paths: generated_paths):

    with open(data_paths.INPUT_JSON, "r", encoding="utf-8") as f:
        tasks = json.load(f)

    for t in tasks:
        img_url = t["data"]["image"]
        q = parse_qs(urlparse(img_url).query)
        rel_path = q.get("d", [""])[0]
        filename = os.path.basename(rel_path)
        preview_rel = data_paths.PREVIEW_DIR / filename
        t["data"]["preview"] = f"/data/local-files/?d={preview_rel}"

    with open(data_paths.OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

    data_paths.INPUT_JSON.unlink()


if __name__ == "__main__":
    for fodler in folders:

        data_path = generate_paths(fodler)

        # export_to_label_studio(data_path)
        label_studio_converter(data_path)
        add_preview_to_json(data_path)
