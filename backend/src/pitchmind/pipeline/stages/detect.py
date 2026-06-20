from __future__ import annotations

from dataclasses import asdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

    import numpy as np
    import pandas as pd

    from pitchmind.cv.detectors.base import Detection, Detector


def detect(
    frame_iter: Iterator[tuple[int, float, np.ndarray]],
    detector: Detector,
    batch_size: int,
) -> pd.DataFrame:
    import pandas as pd  # lazy — requires cv extras

    all_detections: list = []
    batch_imgs: list = []
    batch_meta: list[tuple[int, float]] = []

    for idx, ts, img in frame_iter:
        batch_imgs.append(img)
        batch_meta.append((idx, ts))
        if len(batch_imgs) >= batch_size:
            all_detections.extend(detector.predict(batch_imgs, batch_meta))
            batch_imgs, batch_meta = [], []

    if batch_imgs:
        all_detections.extend(detector.predict(batch_imgs, batch_meta))

    if not all_detections:
        return pd.DataFrame(
            columns=["frame_idx", "timestamp_s", "cls", "cls_name", "conf", "x1", "y1", "x2", "y2"]
        )

    return pd.DataFrame([asdict(d) for d in all_detections])
