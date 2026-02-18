from lib.logic.move_to_destination import Move
from lib.logic.mining import Mining
from lib.logic.dock import Dock
from lib.other.snapshot import SharedState

class Bot():

    def __init__(self, yolo_buffer: SharedState):
        
        self.yolo_buffer = yolo_buffer
        self.move = Move(yolo_buffer)
        self.mining = Mining(yolo_buffer)
        self.dock = Dock(yolo_buffer)
