import os
from label_studio_sdk import LabelStudio
import cv2 as cv
from pathlib import Path
import re
from functools import cache
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from math import inf
from collections import namedtuple
from cv_eve.lib.label_studio_classes.annotations import Annotations
from cv_eve.lib.config import Config
import json
import threading
from datetime import datetime
import logging


cv.setNumThreads(1)


default_labels = [
    {
        "x": 0,
        "y": 8.06289629231319e-14,
        "width": 1.7402293197403491,
        "height": 99.99999999999984,
        "rotation": 0,
        "rectanglelabels": ["UI: Sidebar"],
        "score": 1,
    },
    {
        "x": 43.333333333333336,
        "y": 85.33333333333334,
        "width": 15,
        "height": 13.333333333333334,
        "rotation": 0,
        "rectanglelabels": ["UI: Ship infopanel"],
        "score": 1,
    },
]


class EditAnnotationsAPI():

    config = Config()

    def __init__(self, project_name=config.get("project_name"), workers=config.get("workers")):
        self.client = LabelStudio(
            base_url="http://localhost:8080", api_key=os.environ["LABEL_STUDIO_API_KEY"]
        )
        self.project_name = project_name
        self.workers = workers

    def add_annotation(self, annotations_list, from_id_task=0, to_id_task=inf):
        def process_task(task):
            annotations = Annotations(self.client, task)
            for ann in annotations_list:
                annotations.add(ann)
            annotations.write()
        self.start_process_tasks(process_task, from_id_task, to_id_task)

    def leave_only_better(self, label_name="", from_id_task=0, to_id_task=inf):
        def process_task(task):
            annotations = Annotations(self.client, task)
            annotations.leave_only_better(label_name)
            annotations.write()
        self.start_process_tasks(process_task, from_id_task, to_id_task, "leave_only_better")

    def delete_annotation(self, label_name, from_id_task=0, to_id_task=inf):
        
        def process_task(task):
            annotations_list = task.annotations[0]["result"]
            annotations_update_list = list()
            for ann in annotations_list:
                if label_name not in ann["value"]["rectanglelabels"]:
                    annotations_update_list.append(ann)
            if len(annotations_list) != len(annotations_update_list):
                self.client.annotations.update(task.annotations_ids, result=annotations_update_list)

        self.start_process_tasks(process_task, from_id_task, to_id_task)

    def delete_all_annotations(self, from_id_task=0, to_id_task=inf):

        def process_task(task):
            self.client.annotations.delete(task.annotations_ids)

        self.start_process_tasks(process_task, from_id_task, to_id_task)

    def delete_overlap(self, label_name=None, tolerance = 0.90, from_id_task=0, to_id_task=inf):

        def process_task(task):
            for annotations_in_task in task.annotations:
                start_from = 0
                annotations_update_list = list()
                for annotation_1 in annotations_in_task["result"]:
                    start_from += 1
                    add_annotation = True
                    for annotation_2 in annotations_in_task["result"][start_from:]:
                        value_1 = annotation_1["value"]
                        value_2 = annotation_2["value"]
                        
                        x_a, y_a, w_a, h_a = value_1["x"], value_1["y"], abs(value_1["width"]), abs(value_1["height"])
                        x_b, y_b, w_b, h_b = value_2["x"], value_2["y"], abs(value_2["width"]), abs(value_2["height"])

                        x_a2, y_a2 = x_a + w_a, y_a + h_a
                        x_b2, y_b2 = x_b + w_b, y_b + h_b

                        inter_x, inter_y = max(x_a, x_b), max(y_a, y_b)
                        inter_x2, inter_y2 = min(x_a2, x_b2), min(y_a2, y_b2)

                        inter_w = max(0, inter_x2 - inter_x)
                        inter_h = max(0, inter_y2 - inter_y)
                        
                        inter_s = inter_w * inter_h
                        if inter_s > 0:
                            s_b = w_b * h_b
                            if inter_s/s_b > tolerance:
                                add_annotation = False

                    if add_annotation:
                        annotations_update_list.append(annotation_1)

                if len(annotations_in_task["result"]) != len(annotations_update_list):
                    self.client.annotations.update(task.annotations_ids, result=annotations_update_list)
        
        self.start_process_tasks(process_task, from_id_task, to_id_task)

    def rename_label(self, label_From, label_to):

        def process_task(task):
            annotations_list = task.annotations[0]["result"]
            for ann in annotations_list:
                if label_From in ann["value"]["rectanglelabels"]:
                    ann["value"]["rectanglelabels"] = [label_to]
                    self.client.annotations.update(task.annotations_ids, result=annotations_list)

        self.start_process_tasks(process_task)

    @cache
    def get_project_by_name(self, project_name):
        response = self.client.projects.list()
        for item in response:
            if item.title == project_name:
                return item
            
    def find_elements_by_template(self, template_path, label_name, threshold=0.75, from_id_task=0, to_id_task=inf):

        ann_template = {
            "rotation": 0,
            "rectanglelabels": [label_name],
        }

        if isinstance(template_path, str):
            template_path = [template_path]

        temp_tulp = namedtuple("temp_tulp", ["template", "w", "h"])
        templates_list = list()

        for tem in template_path:
            template = cv.imread(tem, cv.IMREAD_GRAYSCALE)
            assert template is not None, "file could not be read, check with os.path.exists()"
            w, h = template.shape[::-1]
            templates_list.append(temp_tulp(template, w, h))

        def process_task(task):
            base_dir = Path(r"D:\Datasets")
            image_path = Path(re.sub(r"/data/local-files/\?d=", "", task.data["image"]))

            img = cv.imread(str(base_dir / image_path), cv.IMREAD_GRAYSCALE)
            assert img is not None, "file could not be read, check with os.path.exists()"

            best_score = 0
            best_max_loc = None
            best_template = None
            for template in templates_list:
                res = cv.matchTemplate(img, template.template, cv.TM_CCOEFF_NORMED)
                _, max_val, _, max_loc = cv.minMaxLoc(res)

                if max_val > best_score:
                    best_score = max_val
                    best_max_loc = max_loc
                    best_template = template

            if best_score >= threshold:
                top_left = best_max_loc
                annotations_list = task.annotations[0]["result"] if task.annotations else list()
                ann_template_copy = ann_template.copy()
                ann_template_copy.update(
                    {
                        "x": top_left[0]/1920 * 100,
                        "y": top_left[1]/1200 * 100,
                        "width": best_template.w/1920 * 100,
                        "height": best_template.h/1200 * 100,
                        "rotation": 0,
                        "score": best_score
                    }
                )
                annotations_list.append(
                    {
                        "original_width": 1920,
                        "original_height": 1200,
                        "image_rotation": 0,
                        "value": ann_template_copy,
                        "from_name": "label",
                        "to_name": "image",
                        "type": "rectanglelabels",
                    }
                )
                if task.annotations:
                    self.client.annotations.update(task.annotations_ids, result=annotations_list)
                else:
                    self.client.annotations.create(task.id, result=annotations_list)

        self.start_process_tasks(process_task, from_id_task, to_id_task)

    def start_process_tasks(self, process_task, from_id_task=0, to_id_task=inf, desc_add=""):
        project = self.get_project_by_name(self.project_name)
        resp = self.client.tasks.list(project=project.id, page_size=100, fields="all")

        future_to_task_id = {}
        with ThreadPoolExecutor(self.workers) as ex:
            future_to_task_id = {}
            for task in resp:
                if from_id_task <= task.id <= to_id_task:
                    fut = ex.submit(process_task, task)
                    future_to_task_id[fut] = task.id
            with tqdm(total=len(future_to_task_id), desc=" ".join(["Processing", desc_add]), unit="task") as pbar:
                for f in as_completed(future_to_task_id):
                    try:
                        f.result()
                    except Exception:
                        task_id = future_to_task_id[f]
                        logging.exception("Task failed (task_id=%s)", task_id)
                    pbar.update(1)

    def restore_backup(self, file=None, from_id_task=0, to_id_task=inf):
        
        backup_folder = Path(self.config.get("utils_backup_folder"))
        if file is None:
            file = "bwaefwa"
        backup_data = None
        with open(backup_folder / file, "r", encoding="cp1251") as bk_an:
            backup_data = json.load(bk_an)

        id_result_dict = {data['annotations_ids']: data["annotations"][0]["result"] for data in backup_data}
        def process_task(task):
            self.client.annotations.update(task.annotations_ids, result=id_result_dict[task.annotations_ids])

        self.start_process_tasks(process_task, from_id_task, to_id_task, "restore_backup")

    def make_backup(self, from_id_task=0, to_id_task=inf):

        lock = threading.Lock()
        
        backup_list = list()
        def process_task(task):
            with lock:
                backup_list.append({"id": task.id,
                                    "annotations_ids": task.annotations_ids,
                                    "annotations": task.annotations})
            
        self.start_process_tasks(process_task, from_id_task, to_id_task, "make_backup")
        backup_folder = Path(self.config.get("utils_backup_folder"))
        os.makedirs(backup_folder, exist_ok=True)
        datetime_str = datetime.today().strftime(r"%d_%m_%Y_%H_%M_%S")
        with open(backup_folder / f"backup_annotations{datetime_str}.json", "w", encoding="utf-8") as bk_an:
            json.dump(backup_list, bk_an, ensure_ascii=False, indent=2)


config = Config()
edit_annotations_api = EditAnnotationsAPI("EVE-Images")

# edit_annotations_api.restore_backup("backup_annotations07_01_2026_01_14_26.json")
# edit_annotations_api.make_backup()
# edit_annotations_api.delete_all_annotations(from_id_task=14412)
# edit_annotations_api.add_annotation(default_labels, from_id_task=14412)
# edit_annotations_api.delete_overlap()
# edit_annotations_api.rename_label("UI: OVerview panel", "UI: Overview panel")

# tempaltes = config.get("templates")
#label, template = "UI: Overview panel", tempaltes["UI: Overview panel"]
# for label, template in tempaltes.items():
#     edit_annotations_api.find_elements_by_template(template, label, from_id_task=14524)
edit_annotations_api.leave_only_better()
