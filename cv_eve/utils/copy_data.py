import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Папка с исходными файлами
src_folder = "data/mining_asteroid_01"

# Папка, куда копируем
dst_folder = "data/mining_asteroid_01"
sub_folder = "val"

for dir in ["images", "labels"]:
    os.makedirs(os.path.join(BASE_DIR, dst_folder, dir, sub_folder), exist_ok=True)  # создаст папку, если её нет

# Список файлов

for dir in ["images", "labels"]:
    files = [f for f in os.listdir(os.path.join(BASE_DIR, src_folder, dir))
              if os.path.isfile(os.path.join(BASE_DIR, src_folder, dir, f))]
    files.sort()

    # Берём каждый 5-й файл
    every_fifth = files[::52]

    # Копируем
    for f in every_fifth:
        src = os.path.join(BASE_DIR, src_folder, dir, f)
        dst = os.path.join(BASE_DIR, dst_folder, dir, sub_folder, f)
        shutil.copy2(src, dst)  # copy2 сохраняет дату и метаданные
        print(f"Скопирован: {f}")
