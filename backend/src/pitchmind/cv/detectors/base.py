from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    import numpy as np


@dataclass
class Detection:
    frame_idx: int
    timestamp_s: float
    cls: int
    cls_name: str
    conf: float
    x1: float
    y1: float
    x2: float
    y2: float


class Detector(Protocol):
    def predict(
        self,
        frames: list[np.ndarray],
        frame_meta: list[tuple[int, float]],
    ) -> list[Detection]: ...
