from dataclasses import dataclass
import threading
import numpy as np
import torch
import queue
from ultralytics.engine.results import Results


@dataclass(frozen=True)
class Snapshot:
    frame_bgr: np.ndarray
    res: Results


class SharedState:
    def __init__(self):
        self._lock = threading.Lock()
        self._snapshot = queue.Queue(maxsize=1)

    def update(self, snap: Snapshot):
        try:
            self._snapshot.put_nowait(snap)
        except queue.Full:
            pass

    def get(self) -> Snapshot | None:
        return self._snapshot.get()
