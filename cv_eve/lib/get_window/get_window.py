import win32gui
import ctypes
ctypes.windll.user32.SetProcessDPIAware()


class GetWindow():

    def __init__(self, label):
        self.label = label
        self.window = win32gui.FindWindow(None, label)

    def get_region(self):
        left, top, right, bottom = win32gui.GetWindowRect(self.window)
        return left, top, right, bottom
