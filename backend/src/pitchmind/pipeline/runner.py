from __future__ import annotations

import tempfile
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any

import structlog
from sqlalchemy import select, update

from pitchmind.config import settings
from pitchmind.db.models.video_upload import VideoUpload

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine

log = structlog.get_logger(__name__)


def run_pipeline(upload_id: str, engine: Engine) -> None:
    from pitchmind.cv.detectors.yolov11 import YoloV11Detector
    from pitchmind.pipeline.stages.detect import detect
    from pitchmind.pipeline.stages.probe import probe
    from pitchmind.pipeline.stages.sample import sample_frames
    from pitchmind.storage.sync_client import download_file_sync, upload_file_sync

    storage_key = _get_storage_key(upload_id, engine)
    log.info("pipeline.start", upload_id=upload_id, storage_key=storage_key)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        video_path = tmp / "video"

        log.info("pipeline.downloading", upload_id=upload_id)
        download_file_sync(storage_key, video_path)

        log.info("pipeline.probing", upload_id=upload_id)
        probe_result = probe(video_path)
        _update_duration(upload_id, probe_result.duration_s, engine)
        log.info(
            "pipeline.probe_done",
            upload_id=upload_id,
            fps=probe_result.fps,
            duration_s=probe_result.duration_s,
            width=probe_result.width,
            height=probe_result.height,
        )

        log.info("pipeline.detecting", upload_id=upload_id, model=settings.cv_yolo_model)
        detector = YoloV11Detector(settings.cv_yolo_model, settings.cv_device)
        frames = sample_frames(video_path, settings.cv_detection_fps)
        df = detect(frames, detector, settings.cv_batch_size)
        log.info("pipeline.detect_done", upload_id=upload_id, total_detections=len(df))

        parquet_path = tmp / "detections.parquet"
        df.to_parquet(parquet_path, index=False)
        artifact_key = f"artifacts/{upload_id}/detections.parquet"
        upload_file_sync(parquet_path, artifact_key, "application/octet-stream")
        log.info("pipeline.artifact_uploaded", upload_id=upload_id, key=artifact_key)

        sampled = int(df["frame_idx"].nunique()) if not df.empty else 0
        summary = {
            "cv": {
                "model": settings.cv_yolo_model,
                "device": settings.cv_device,
                "fps_sample": settings.cv_detection_fps,
                "video_fps": probe_result.fps,
                "duration_s": probe_result.duration_s,
                "width": probe_result.width,
                "height": probe_result.height,
                "total_frames_sampled": sampled,
                "total_detections": len(df),
                "artifact_key": artifact_key,
            }
        }
        _update_meta(upload_id, summary, engine)


def _get_storage_key(upload_id: str, engine: Engine) -> str:
    with engine.connect() as conn:
        row = conn.execute(
            select(VideoUpload.storage_key).where(VideoUpload.id == uuid.UUID(upload_id))
        ).one()
    return str(row.storage_key)


def _update_duration(upload_id: str, duration_s: float, engine: Engine) -> None:
    with engine.begin() as conn:
        conn.execute(
            update(VideoUpload)
            .where(VideoUpload.id == uuid.UUID(upload_id))
            .values(duration_seconds=duration_s)
        )


def _update_meta(upload_id: str, meta: dict[str, Any], engine: Engine) -> None:
    with engine.begin() as conn:
        conn.execute(
            update(VideoUpload).where(VideoUpload.id == uuid.UUID(upload_id)).values(meta=meta)
        )
