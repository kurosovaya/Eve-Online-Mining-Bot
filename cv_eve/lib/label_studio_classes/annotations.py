from cv_eve.lib.config import Config

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
        only_once_per_task_list = Config().get("only_once_per_task")
        for ann in self.ann_list:
            if ann["value"]["rectanglelabels"][0] not in only_once_per_task_list:
                updated_list.append(ann)
                continue
            ann_item = AnnotationItem(ann)
            if label_name and ann["value"]["rectanglelabels"] != [label_name]:
                updated_list.append(ann)
                continue
            best_score_item = best_score_by_key.get(ann["value"]["rectanglelabels"][0])
            best_score_key = ann["value"]["rectanglelabels"][0]
            if best_score_item is None:
                best_score_by_key[best_score_key] = ann
                if ann_item.get_score() is None:
                    best_score_by_key[best_score_key]["value"]["score"] = 0.5
                continue
            if ann_item.get_score() is None:
                ann["value"]["score"] = 0.5
            if AnnotationItem(ann).get_score() > AnnotationItem(best_score_item).get_score():
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


class AnnotationItem():


    def __init__(self, annotation):
        self.annotation = annotation

    def get_score(self):

        try:
            score = self.annotation["value"].get("score") or self.annotation.get("score")
            return score
        except ValueError as e:
            print("ERROR get_score:", e)

            return None
