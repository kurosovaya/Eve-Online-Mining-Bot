from dataclasses import dataclass
import threading
import numpy as np

@dataclass(frozen=True)
class Snapshot:
    t: float
    frame: np.ndarray          # BGR image
    detections: object         # boxes/masks/whatever you store

class SharedState:
    def __init__(self):
        self._lock = threading.Lock()
        self._snapshot: Snapshot | None = None

    def update(self, snap: Snapshot):
        with self._lock:
            self._snapshot = snap

    def get(self) -> Snapshot | None:
        with self._lock:
            return self._snapshot
