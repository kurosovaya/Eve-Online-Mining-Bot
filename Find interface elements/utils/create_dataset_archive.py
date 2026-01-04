from zipfile import ZipFile, ZIP_DEFLATED
from pathlib import Path
import os
import json

BASE_DIR = Path(__file__).resolve().parent
os.chdir(BASE_DIR)

with open(r"D:\Datasets\EVE-images\notes.json", "r") as fr, open("classes_indexes.txt", "w") as fw:
    notes = json.load(fr)
    categories = notes["categories"]
    fw.writelines(f"{item['id']}: \"{item['name']}\"\n" for item in categories)

# os.makedirs(r".\dataset_archive", exist_ok=True)
# yolo_export_path = Path(r"C:\Users\Kurosovaya\Downloads\project-5-at-2025-12-31-23-01-9c0b0e16.zip")
# with ZipFile("dataset_archive\out.zip", "w", compression=ZIP_DEFLATED, compresslevel=3) as z:
#     for p in src.rglob("*"):
#         if p.is_file():
#             z.write(p, arcname=p.relative_to(src))
