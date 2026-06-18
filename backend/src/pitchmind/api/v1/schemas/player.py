import uuid
from datetime import date

from pydantic import BaseModel, Field

from pitchmind.db.models.player import PlayerPosition


class PlayerCreate(BaseModel):
    team_id: uuid.UUID | None = None
    name: str = Field(min_length=1, max_length=200)
    position: PlayerPosition
    nationality: str | None = Field(default=None, max_length=100)
    date_of_birth: date | None = None
    jersey_number: int | None = Field(default=None, ge=1, le=99)


class PlayerResponse(BaseModel):
    id: uuid.UUID
    team_id: uuid.UUID | None
    name: str
    position: PlayerPosition
    nationality: str | None
    date_of_birth: date | None
    jersey_number: int | None
    is_active: bool

    model_config = {"from_attributes": True}
