from lazy_ls.utils.export_to_label_studio import ExportToLabelStudio
from lazy_ls.utils.ffmpeg import ConvertVideo


# ConvertVideo(r"D:\Datasets\EVE-images\data\video", r"D:\Datasets\EVE-images").convert("2026-01-16_22-25-35.mkv", 0.03)

export_to_label_studio = ExportToLabelStudio() 
# export_to_label_studio.split_into_folders(r"D:\Datasets\EVE-images\2026-01-16_22-25-35\images")

export_to_label_studio.label_studio_converter("2026-01-16_22-25-35")
