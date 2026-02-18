from lib.other.snapshot import SharedState
from lib.logic.annotated_area_handler import AnnotatedArea, AnnotatedLabels
import cv2 as cv
import logging
import numpy as np
import pyautogui


logger = logging.getLogger(__name__)


class Dock:
    def __init__(self, yolo_buffer: SharedState):
        self.yolo_buffer = yolo_buffer

    def highpass(self, gray: np.ndarray) -> np.ndarray:
        blur = cv.GaussianBlur(gray, (0, 0), 5)
        hp = cv.addWeighted(gray, 1.5, blur, -0.5, 0)
        return hp

    def undock(self):
        logger.info("Trying to undock")
        area, coords = AnnotatedArea(self.yolo_buffer).get_area(
            AnnotatedLabels.UI_STATION_INFOPANEL
        )
        undock_template = cv.imread(
            r"D:\Projects\Eve-Online-Mining-Bot\cv_eve\lib\logic\buttons_images\undock.png"
        )
        img_h, template_h = self.highpass(area), self.highpass(undock_template)
        res = cv.matchTemplate(img_h, template_h, cv.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv.minMaxLoc(res)
        # мож чет типа контролов сдедлать? ControlsButton()
        x_middle = max_loc[0] + undock_template.shape[1] // 2
        y_middle = max_loc[1] + undock_template.shape[0] // 2
        pyautogui.moveTo(coords[0] + x_middle, coords[1] + y_middle)
        pyautogui.click()
        logger.info("Succesufely undoking")

    def dock():
        pass
