from pathlib import Path

labels_dir = Path(r"D:\Datasets\EVE-images\mining_asteroid_01\labels\train")
labels_obb_dir = labels_dir.with_name(labels_dir.name + "_obb")

labels_obb_dir.mkdir(exist_ok=True)
for label in labels_dir.glob("*.txt"):
    with open(label, "r") as f_in,\
         open(labels_obb_dir / label.name, "w") as f_out:
        lines_obb = []
        for line in f_in.readlines():
            line_split = [float(x) for x in line.strip().split()]
            if len(line_split) < 5:
                continue
            indx, cx, cy, width, height = [float(x) for x in line.strip().split()][:5]
            w2 = width / 2
            h2 = height / 2
            
            x1, y1 = cx - w2, cy - h2
            x2, y2 = cx + w2, cy - h2
            x3, y3 = cx + w2, cy + h2
            x4, y4 = cx - w2, cy + h2
            lines_obb.append(" ".join(str(x) for x in [int(indx), x1, y1, x2, y2, x3, y3, x4, y4] ) + "\n")
        f_out.writelines(lines_obb)
