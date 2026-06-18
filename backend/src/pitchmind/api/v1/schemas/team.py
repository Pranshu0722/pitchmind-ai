import uuid

from pydantic import BaseModel, Field


class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    short_name: str | None = Field(default=None, max_length=10)
    country: str = Field(min_length=1, max_length=100)
    founded_year: int | None = Field(default=None, ge=1800, le=2100)
    logo_url: str | None = None
    stadium_name: str | None = Field(default=None, max_length=200)


class TeamResponse(BaseModel):
    id: uuid.UUID
    name: str
    short_name: str | None
    country: str
    founded_year: int | None
    logo_url: str | None
    stadium_name: str | None

    model_config = {"from_attributes": True}
