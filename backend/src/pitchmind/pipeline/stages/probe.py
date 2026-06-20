from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProbeResult:
    fps: float
    duration_s: float
    width: int
    height: int
    total_frames: int


def probe(video_path: Path) -> ProbeResult:
    import cv2  # lazy — requires cv extras

    cap = cv2.VideoCapture(str(video_path))
    try:
        fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    finally:
        cap.release()

    return ProbeResult(
        fps=fps,
        duration_s=total / fps if fps else 0.0,
        width=width,
        height=height,
        total_frames=total,
    )
