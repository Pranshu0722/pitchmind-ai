import uuid

import dramatiq
import structlog
from sqlalchemy import create_engine, update

from pitchmind.config import settings
from pitchmind.db.models.video_upload import UploadStatus, VideoUpload

log = structlog.get_logger(__name__)

# Convert asyncpg URL to psycopg2 for sync access inside Dramatiq workers
_SYNC_URL = settings.database_url.replace("+asyncpg", "+psycopg2")
_engine = create_engine(_SYNC_URL, pool_pre_ping=True)


def _set_status(upload_id: str, upload_status: UploadStatus) -> None:
    with _engine.begin() as conn:
        conn.execute(
            update(VideoUpload)
            .where(VideoUpload.id == uuid.UUID(upload_id))
            .values(status=upload_status)
        )


@dramatiq.actor(queue_name="video")
def process_video(upload_id: str) -> None:
    from pitchmind.pipeline.runner import run_pipeline  # lazy — cv extras only in worker

    log.info("video.processing.start", upload_id=upload_id)
    _set_status(upload_id, UploadStatus.PROCESSING)
    try:
        run_pipeline(upload_id, _engine)
        _set_status(upload_id, UploadStatus.READY)
        log.info("video.processing.done", upload_id=upload_id)
    except Exception:
        _set_status(upload_id, UploadStatus.FAILED)
        log.exception("video.processing.failed", upload_id=upload_id)
        raise
