import uuid
from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from pitchmind.db.models.match import MatchStatus


class MatchCreate(BaseModel):
    home_team_id: uuid.UUID
    away_team_id: uuid.UUID
    kickoff_at: datetime
    venue: str | None = Field(default=None, max_length=200)
    competition: str | None = Field(default=None, max_length=100)
    season: str | None = Field(default=None, max_length=20)

    @model_validator(mode="after")
    def teams_must_differ(self) -> "MatchCreate":
        if self.home_team_id == self.away_team_id:
            raise ValueError("home and away teams must be different")
        return self


class MatchUpdate(BaseModel):
    status: MatchStatus | None = None
    home_score: int | None = Field(default=None, ge=0)
    away_score: int | None = Field(default=None, ge=0)


class MatchResponse(BaseModel):
    id: uuid.UUID
    home_team_id: uuid.UUID
    away_team_id: uuid.UUID
    kickoff_at: datetime
    venue: str | None
    status: MatchStatus
    home_score: int
    away_score: int
    competition: str | None
    season: str | None

    model_config = {"from_attributes": True}
