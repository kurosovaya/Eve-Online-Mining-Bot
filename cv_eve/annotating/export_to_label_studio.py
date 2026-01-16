from lazy_ls.utils.export_to_label_studio import ExportToLabelStudio
from lazy_ls.utils.ffmpeg import ConvertVideo


# ConvertVideo(r"D:\Datasets\EVE-images\data\video", r"D:\Datasets\EVE-images").convert("2026-01-12 23-22-21.mkv")
folders = [
    "2026-01-12 23-22-21"
]

for fodler in folders:
    export_to_label_studio = ExportToLabelStudio() 
    # export_to_label_studio.split_into_folders(r"D:\Datasets\EVE-images\2026-01-12 23-22-21\images")
    data_path = export_to_label_studio.generate_paths(fodler, "part_0001")
    export_to_label_studio.label_studio_converter(data_path)
