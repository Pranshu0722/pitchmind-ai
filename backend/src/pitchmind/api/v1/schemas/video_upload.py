import uuid
from datetime import datetime

from pydantic import BaseModel

from pitchmind.db.models.video_upload import UploadStatus


class VideoUploadResponse(BaseModel):
    id: uuid.UUID
    match_id: uuid.UUID | None
    uploaded_by: uuid.UUID
    filename: str
    file_size_bytes: int
    content_type: str
    status: UploadStatus
    duration_seconds: float | None
    created_at: datetime

    model_config = {"from_attributes": True}


class PresignedUrlResponse(BaseModel):
    url: str
    expires_in_seconds: int = 3600
