from lazy_ls.config.config import Config
from lazy_ls.utils.edit_annotations import EditAnnotationsAPI
from lazy_ls.label_studio_classes.task import Task
from label_studio_sdk import LabelStudio
import os

default_labels_1200 = [
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

default_labels_1080 = [
    {
        "x": 0,
        "y": 0,
        "width": 2.2132897547688692,
        "height": 100,
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
    {
        "x": 32.13745878774791,
        "y": 62.933204631322326,
        "width": 30.34278431012717,
        "height": 36.97845927943369,
        "rotation": 0,
        "rectanglelabels": ["UI: Chat"],
        "score": 1,
    },
    {
        "x": 3.9996263599276585,
        "y": 62.88241285452777,
        "width": 28.005439440575202,
        "height": 37.001229845138525,
        "rotation": 0,
        "rectanglelabels": ["UI: Warehouse"],
        "score": 1,
    },
    {
        "x": 2.6752353522841723,
        "y": 4.079297926900086,
        "width": 14.228790859401588,
        "height": 17.102606485806373,
        "rotation": 0,
        "rectanglelabels": ["UI: Navigation"],
        "score": 1,
    },
    {
        "x": 74.86425928112656,
        "y": 1.491525403545089,
        "width": 24.289612654939805,
        "height": 13.874646722243696,
        "rotation": 0,
        "rectanglelabels": ["UI: Selected object"],
        "score": 1,
    },
    {
        "x": 74.86825453265972,
        "y": 15.538847430939255,
        "width": 24.274380312614603,
        "height": 57.04368453784119,
        "rotation": 0,
        "rectanglelabels": ["UI: Overview panel"],
        "score": 1,
    },
    {
        "x": 97.73063349055263,
        "y": 96.05211364471398,
        "width": 1.4788512366229924,
        "height": 2.6114553463545764,
        "rotation": 0,
        "rectanglelabels": ["UI: Notifications"],
        "score": 1,
    }
]

config = Config()
edit_annotations_api = EditAnnotationsAPI()

# edit_annotations_api.restore_backup("backup_annotations07_01_2026_01_14_26.json")
# edit_annotations_api.make_backup()

# tempaltes = config.get("templates")
# edit_annotations_api.delete_annotation('UI: Ship infopanel', 18445)
# edit_annotations_api.delete_annotation('UI: Ship infopanel', 18021, 18076)
# edit_annotations_api.delete_all_annotations(from_id_task=18021)
#edit_annotations_api.find_elements_by_template(tempaltes, 0.55, from_id_task=18547)
# client = LabelStudio(
#             base_url="http://localhost:8080", api_key=os.environ["LABEL_STUDIO_API_KEY"]
#         )



edit_annotations_api.update_fields_by_function_task(from_id_task=17000)
# annotations = Task(client, 19113).get_annotations()
# annotations_values = annotations.values()
# edit_annotations_api.add_annotation(annotations_values, from_id_task=19114)
# edit_annotations_api.leave_only_better(from_id_task=19114)
