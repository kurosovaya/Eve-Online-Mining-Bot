from pathlib import Path
import yaml

convert_dirs = [r"D:\Datasets\EVE-images\Ready\2025-09-17_17-13-08\pred\labels_obb",
                r"D:\Datasets\EVE-images\Ready\2025-09-17_17-13-08\pred2\labels_obb",
                r"D:\Datasets\EVE-images\Ready\mining_asteroid_01\labels\train_obb",
                r"D:\Datasets\EVE-images\Ready\mining_asteroid_01\labels\val_obb",
                r"D:\Datasets\EVE-images\Ready\ui_01\labels\train_obb",
                r"D:\Datasets\EVE-images\Ready\ui_01\labels\val_obb"]
reference = Path(r"D:\Projects\Eve-Online-Mining-Bot\Find interface elements\utils\classes.yaml")
with open(reference, encoding="utf-8") as file:
    reference_load = yaml.safe_load(file)
convert_dict = {"Text": 0,
                   "UI": 1,
                   "Asteroid": 2,
                   "My ship": 3,
                   "Ship": 4,
                   "Planet": 5}
reference_dict = {}
for key, item in reference_load["names"].items():
    reference_dict[item] = key

REMAP = {}

for item, key in reference_dict.items():
    if not(convert_dict.get(item) is None):
        REMAP[convert_dict.get(item)] = key
    else:
        REMAP[key] = key


for dir in convert_dirs:
    for txt in Path(dir).rglob("*.txt"):
        lines = txt.read_text(encoding="utf-8").splitlines()
        out = []
        for ln in lines:
            if not ln.strip():
                continue
            parts = ln.split()
            old = int(parts[0])
            if old not in REMAP:
                continue
            parts[0] = str(REMAP[old])
            out.append(" ".join(parts))
        txt.write_text("\n".join(out), encoding="utf-8")
    print("Done")
