from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pitchmind.cv.detectors.base import Detection

if TYPE_CHECKING:
    import numpy as np


class YoloV11Detector:
    def __init__(self, model_name: str, device: str) -> None:
        from ultralytics import YOLO  # lazy — requires cv extras

        self._model: Any = YOLO(model_name)
        self._device = device

    def predict(
        self,
        frames: list[np.ndarray],
        frame_meta: list[tuple[int, float]],
    ) -> list[Detection]:
        results = self._model.predict(frames, device=self._device, verbose=False)
        detections: list[Detection] = []
        for result, (fidx, ts) in zip(results, frame_meta, strict=True):
            for box in result.boxes:
                detections.append(
                    Detection(
                        frame_idx=fidx,
                        timestamp_s=ts,
                        cls=int(box.cls[0]),
                        cls_name=result.names[int(box.cls[0])],
                        conf=float(box.conf[0]),
                        x1=float(box.xyxy[0][0]),
                        y1=float(box.xyxy[0][1]),
                        x2=float(box.xyxy[0][2]),
                        y2=float(box.xyxy[0][3]),
                    )
                )
        return detections
