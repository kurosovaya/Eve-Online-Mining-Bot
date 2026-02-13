from lazy_ls.utils.export_to_label_studio import ExportToLabelStudio
from lazy_ls.utils.ffmpeg import ConvertVideo
from pathlib import Path


file_name = Path("2026-02-11_17-20-28.mkv")
ConvertVideo(r"D:\Datasets\EVE-images\data\video", r"D:\Datasets\EVE-images").convert(file_name, 0.02)
export_to_label_studio = ExportToLabelStudio() 
export_to_label_studio.split_into_folders(fr"D:\Datasets\EVE-images\{file_name.stem}\images")
export_to_label_studio.label_studio_converter(file_name.stem)
