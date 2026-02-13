from lazy_ls.utils.export_from_label_studio import ProjectAPI
import json

project_api = ProjectAPI()
project_api.export("YOLO_OBB_WITH_IMAGES")
project_api.prepare_for_kaggle()
project_api.split_yolo_zip_train_val(r"D:\Projects\Eve-Online-Mining-Bot\cv_eve\annotating\exports\project_EVE-Images_YOLO_OBB_WITH_IMAGES.zip", 0.15)
# with ZipFile(r"D:\Projects\Eve-Online-Mining-Bot\cv_eve\annotating\exports\project_EVE-Images_YOLO_OBB_WITH_IMAGES.zip", mode="a") as zip_file:

