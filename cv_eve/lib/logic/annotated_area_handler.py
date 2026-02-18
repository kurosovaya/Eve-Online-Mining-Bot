from lib.other.snapshot import SharedState
from enum import Enum
import numpy as np


class AnnotatedLabels(Enum):

    ASTEROID = "Asteroid"
    PLANET = "Planet"
    SHIP = "Ship"
    TEXT = "Text"
    UI_BOOKMARKS = "UI: Bookmarks"
    UI_CHAT = "UI: Chat"
    UI_CHAT_CHANNELS = "UI: Chat channels"
    UI_NAVIGATION = "UI: Navigation"
    UI_NOTIFICATIONS = "UI: Notifications"
    UI_OVERVIEW_PANEL = "UI: Overview panel"
    UI_SELECTED_OBJECT = "UI: Selected object"
    UI_SHIP_FITTING = "UI: Ship fitting"
    UI_SHIP_INFOPANEL = "UI: Ship infopanel"
    UI_SIDEBAR = "UI: Sidebar"
    UI_STATION_INFOPANEL = "UI: Station infopanel"
    UI_WAREHOUSE = "UI: Warehouse"


class AnnotatedArea():

    def __init__(self, buffer: SharedState):

        self.buffer = buffer

    def get_area(self, area_name: str) -> tuple[np.ndarray, tuple[int, int, int, int]]:
        
        while True:
            snap = self.buffer.get()
            clss_ids = snap.res.obb.cls.numpy().astype(int)
            for i, ids in enumerate(clss_ids):
                if snap.res.names[ids] == area_name.value:
                    x1, y1, x2, y2 = map(int, snap.res.obb.xyxy[i].tolist())
                    return self.crop_xyxy(snap.frame_bgr, x1, y1, x2, y2), (x1, y1, x2, y2)


    def crop_xyxy(self, img: np.ndarray, x1, y1, x2, y2):
        h, w = img.shape[:2]
        x1 = max(0, min(w, int(x1)))
        x2 = max(0, min(w, int(x2)))
        y1 = max(0, min(h, int(y1)))
        y2 = max(0, min(h, int(y2)))
        if x2 <= x1 or y2 <= y1:
            return None
        return img[y1:y2, x1:x2].copy()
