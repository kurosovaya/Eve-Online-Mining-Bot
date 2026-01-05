from copy import deepcopy

class Annotations():

    ann_template = {
            "original_width": 1920,
            "original_height": 1200,
            "image_rotation": 0,
            "value": None,
            "from_name": "label",
            "to_name": "image",
            "type": "rectanglelabels"
    }

    def __init__(self, client, task):
        
        self.client = client
        self.task = task
        self.ann_list = self.task.annotations[0]["result"] if self.task.annotations else list()

    def add(self, ann):

        templ_copy = self.ann_template.copy()
        templ_copy.update({"value": ann})
        self.ann_list.append(templ_copy)

    def leave_only_better(self, label_name=""):

        best_score_by_key = {}
        updated_list = list()
        for ann in self.ann_list:
            if label_name and ann["value"]["rectanglelabels"] != [label_name]:
                updated_list.append(ann)
                continue
            best_score_item = best_score_by_key.get(ann["value"]["rectanglelabels"][0])
            best_score_key = ann["value"]["rectanglelabels"][0]
            if best_score_item is None:
                best_score_by_key[best_score_key] = ann
                continue
            if ann["value"]["score"] > best_score_item["value"]["score"]:
                best_score_by_key[best_score_key] = ann
        
        updated_list.extend(best_score_by_key.values())

        self.ann_list = updated_list

    # def replace(self, rep_ann, condition):

    #     for ann in self.ann_list:


    def write(self):
        if self.task.annotations:
            self.client.annotations.update(self.task.annotations_ids, result=self.ann_list)
        else:
            self.client.annotations.create(self.task.id, result=self.ann_list)
