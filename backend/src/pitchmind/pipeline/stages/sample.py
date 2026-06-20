from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path

    import numpy as np


def sample_frames(
    video_path: Path,
    target_fps: float,
) -> Iterator[tuple[int, float, np.ndarray]]:
    import cv2  # lazy — requires cv extras

    cap = cv2.VideoCapture(str(video_path))
    native_fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    step = max(1, round(native_fps / target_fps))
    frame_idx = 0
    sample_idx = 0
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if frame_idx % step == 0:
                yield sample_idx, frame_idx / native_fps, frame
                sample_idx += 1
            frame_idx += 1
    finally:
        cap.release()
