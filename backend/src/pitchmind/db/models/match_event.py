import uuid
from enum import StrEnum
from typing import Any

from sqlalchemy import Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from pitchmind.db.base import Base, TimestampMixin


class EventType(StrEnum):
    GOAL = "GOAL"
    OWN_GOAL = "OWN_GOAL"
    ASSIST = "ASSIST"
    YELLOW_CARD = "YELLOW_CARD"
    RED_CARD = "RED_CARD"
    SECOND_YELLOW = "SECOND_YELLOW"
    SUBSTITUTION_IN = "SUBSTITUTION_IN"
    SUBSTITUTION_OUT = "SUBSTITUTION_OUT"
    PENALTY_SCORED = "PENALTY_SCORED"
    PENALTY_MISSED = "PENALTY_MISSED"


class MatchEvent(Base, TimestampMixin):
    __tablename__ = "match_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("matches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    player_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("players.id", ondelete="SET NULL"), nullable=True
    )
    event_type: Mapped[EventType] = mapped_column(
        Enum(EventType, name="event_type"), nullable=False, index=True
    )
    minute: Mapped[int] = mapped_column(Integer, nullable=False)
    extra_time_minute: Mapped[int | None] = mapped_column(Integer, nullable=True)
    meta: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    def __repr__(self) -> str:
        return f"<MatchEvent type={self.event_type} minute={self.minute}>"
