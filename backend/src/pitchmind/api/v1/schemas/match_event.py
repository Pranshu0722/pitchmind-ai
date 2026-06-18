import uuid
from typing import Any

from pydantic import BaseModel, Field

from pitchmind.db.models.match_event import EventType


class MatchEventCreate(BaseModel):
    player_id: uuid.UUID | None = None
    event_type: EventType
    minute: int = Field(ge=0, le=130)
    extra_time_minute: int | None = Field(default=None, ge=1)
    meta: dict[str, Any] | None = None


class MatchEventResponse(BaseModel):
    id: uuid.UUID
    match_id: uuid.UUID
    player_id: uuid.UUID | None
    event_type: EventType
    minute: int
    extra_time_minute: int | None
    meta: dict[str, Any] | None

    model_config = {"from_attributes": True}
