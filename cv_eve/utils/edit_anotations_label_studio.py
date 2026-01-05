from pathlib import Path
import json

file_for_edit = Path(r"D:\Datasets\EVE-images\project-5-at-2025-12-13-00-15-06411301.json")
file_for_edit_output = Path(r"D:\Datasets\EVE-images\project-5-at-2025-12-13-00-15-06411301.json")

def change_label(label_from, label_to):
    for task in tasks_dict:
        for annotations_in_task in task["annotations"]:
            for annotation in annotations_in_task["result"]:
                rectanglelabels = annotation["value"]["rectanglelabels"]
                annotation["value"]["rectanglelabels"] = [label_to if label == label_from else label for label in rectanglelabels]


def convert_labels(x_a, y_a, w_a, h_a, label_to, tolerance=0.85):
    for task in tasks_dict:
        for annotations_in_task in task["annotations"]:
            for annotation in annotations_in_task["result"]:
                value = annotation["value"]
                if label_to in value["rectanglelabels"] or annotation['type'] != 'rectanglelabels':
                    continue
                
                x_b, y_b, w_b, h_b = value["x"], value["y"], abs(value["width"]), abs(value["height"])

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
                        value["rectanglelabels"] = [label_to]

def add_sidebar_annotation(add_annotation):
    
    label_name = add_annotation["value"]["rectanglelabels"][0]
    for task in tasks_dict:
        annotation = task["annotations"][0]
        if "result" not in annotation:
            annotation["result"] = []
            
        current_results = annotation["result"]
        
        already_exists = False
        for item in current_results:
            if item.get("type") == "rectanglelabels":
                labels = item.get("value", {}).get("rectanglelabels", [])
                if label_name in labels:
                    already_exists = True
                    break
        
        if already_exists:
            continue
        
        current_results.append(add_annotation)


KEYS_TO_CLEAN = [
    "meta", 
    "inner_id", 
    "total_annotations", 
    "cancelled_annotations", 
    "total_predictions", 
    "comment_count", 
    "unresolved_comment_count", 
    "last_comment_updated_at", 
    "project", 
    "comment_authors",
    "unique_id",
    "id",
    "predictions",
    "prediction",
    "result_count",
    "import_id",
    "task",
    "ground_truth",
    "updated_by",
    "parent_prediction",
    "parent_annotation",
    "drafts",
    "last_created_by",
    "bulk_created",
    "last_action",
    "lead_time",
    "draft_created_at",
    "updated_at",
    "created_at",
    "was_cancelled",
    "completed_by"
]
def delete_metadata():
    for task in tasks_dict:
        for key in KEYS_TO_CLEAN:
            task.pop(key, None)
        for annotations_in_task in task["annotations"]:
            for key in KEYS_TO_CLEAN:
                annotations_in_task.pop(key, None)
            for annotation in annotations_in_task["result"]:
                for key in KEYS_TO_CLEAN:
                    annotation.pop(key, None)

with open(file_for_edit, "r") as file:
    tasks_dict = json.load(file)

sidebar_ann = {
            "original_width": 1920,
            "original_height": 1200,
            "image_rotation": 0,
            "value": {
              "x": 2.0713116131066352e-16,
              "y": 0,
              "width": 1.8656716417910428,
              "height": 98.6940298507462,
              "rotation": 0,
              "rectanglelabels": [
                "UI: Sidebar"
              ]
            },
            "from_name": "label",
            "to_name": "image",
            "type": "rectanglelabels",
            "origin": "manual"
          }

# add_sidebar_annotation(sidebar_ann)
delete_metadata()
# change_label("My ship in hangar", "Ship")
# convert_labels(82.39272388059703, 50.74626865671642, 17.607276119402968, 24.999999999999954, "UI: Bookmarks")
convert_labels(86.23715, 0, 13.194500000000001, 54.246, "UI: Station infopanel", tolerance=0.8)
# convert_labels(1.9173499999999981, 65.45315, 30.44350895522388, 34.546850000000006, "UI: Warehouse")
# convert_labels(0, 0, 1.982276119402985, 100, "UI: Sidebar")
# convert_labels(2.1681104565039817, 3.246927132392858, 12.3718613938586, 8.322355124587846, "UI: Navigation")
# convert_labels(97.77905223535234, 96.50254518465235, 1.396795958898045, 2.1866646549997046, "UI: Notifications")
with open(file_for_edit_output, "w") as file:
    json.dump(tasks_dict, file, indent=2)
