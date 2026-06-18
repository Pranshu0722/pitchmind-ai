# Import all models so Alembic autogenerate and SQLAlchemy mappers see them.
from pitchmind.db.models.audit import AuditLog
from pitchmind.db.models.match import Match, MatchStatus
from pitchmind.db.models.match_event import EventType, MatchEvent
from pitchmind.db.models.player import Player, PlayerPosition
from pitchmind.db.models.team import Team
from pitchmind.db.models.user import User, UserRole
from pitchmind.db.models.video_upload import UploadStatus, VideoUpload

__all__ = [
    "User",
    "UserRole",
    "AuditLog",
    "Team",
    "Player",
    "PlayerPosition",
    "Match",
    "MatchStatus",
    "MatchEvent",
    "EventType",
    "VideoUpload",
    "UploadStatus",
]
