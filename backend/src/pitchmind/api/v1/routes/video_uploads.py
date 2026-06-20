import uuid
from datetime import UTC, datetime

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pitchmind.api.limiter import limiter
from pitchmind.api.v1.schemas.video_upload import PresignedUrlResponse, VideoUploadResponse
from pitchmind.config import settings
from pitchmind.core.deps import get_current_user, require_role
from pitchmind.db.models.user import User, UserRole
from pitchmind.db.models.video_upload import UploadStatus, VideoUpload
from pitchmind.db.session import get_db
from pitchmind.queue import broker as _broker  # noqa: F401 — registers Dramatiq broker
from pitchmind.queue.tasks import process_video
from pitchmind.storage import client as storage

log = structlog.get_logger(__name__)
router = APIRouter()

MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2 GB
ALLOWED_CONTENT_TYPES = {"video/mp4", "video/x-msvideo", "video/quicktime", "video/webm"}


@router.post("/", response_model=VideoUploadResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.rate_limit_upload)
async def upload_video(
    request: Request,
    file: UploadFile,
    match_id: uuid.UUID | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> VideoUpload:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported type. Allowed: {sorted(ALLOWED_CONTENT_TYPES)}",
        )

    data = await file.read()
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File exceeds 2 GB limit"
        )

    await storage.ensure_bucket()

    date_prefix = datetime.now(UTC).strftime("%Y/%m/%d")
    key = f"videos/{date_prefix}/{uuid.uuid4()}/{file.filename}"
    await storage.upload_file(key, data, file.content_type)

    record = VideoUpload(
        id=uuid.uuid4(),
        match_id=match_id,
        uploaded_by=current_user.id,
        filename=file.filename,
        storage_key=key,
        file_size_bytes=len(data),
        content_type=file.content_type,
        status=UploadStatus.PENDING,
    )
    db.add(record)
    await db.flush()
    process_video.send(str(record.id))
    log.info("video.uploaded", upload_id=str(record.id), key=key, size=len(data))
    return record


@router.get("/", response_model=list[VideoUploadResponse])
async def list_uploads(
    match_id: uuid.UUID | None = Query(default=None),
    upload_status: UploadStatus | None = Query(default=None, alias="status"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> list[VideoUpload]:
    stmt = select(VideoUpload).order_by(VideoUpload.created_at.desc()).offset(skip).limit(limit)
    if match_id is not None:
        stmt = stmt.where(VideoUpload.match_id == match_id)
    if upload_status is not None:
        stmt = stmt.where(VideoUpload.status == upload_status)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{upload_id}", response_model=VideoUploadResponse)
async def get_upload(upload_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> VideoUpload:
    result = await db.execute(select(VideoUpload).where(VideoUpload.id == upload_id))
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found")
    return record


@router.get("/{upload_id}/download", response_model=PresignedUrlResponse)
async def get_download_url(
    upload_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> PresignedUrlResponse:
    result = await db.execute(select(VideoUpload).where(VideoUpload.id == upload_id))
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found")

    url = await storage.get_presigned_url(record.storage_key)
    return PresignedUrlResponse(url=url)


@router.delete(
    "/{upload_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(UserRole.ADMIN))],
)
async def delete_upload(upload_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> None:
    result = await db.execute(select(VideoUpload).where(VideoUpload.id == upload_id))
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload not found")

    await storage.delete_file(record.storage_key)
    await db.delete(record)
    await db.flush()
    log.info("video.deleted", upload_id=str(upload_id))
