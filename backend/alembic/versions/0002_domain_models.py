"""domain models: teams, players, matches, match_events

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    player_position_enum = postgresql.ENUM(
        "GK", "DEF", "MID", "FWD", name="player_position", create_type=True
    )
    player_position_enum.create(op.get_bind(), checkfirst=True)

    match_status_enum = postgresql.ENUM(
        "SCHEDULED",
        "LIVE",
        "FINISHED",
        "CANCELLED",
        "POSTPONED",
        name="match_status",
        create_type=True,
    )
    match_status_enum.create(op.get_bind(), checkfirst=True)

    event_type_enum = postgresql.ENUM(
        "GOAL",
        "OWN_GOAL",
        "ASSIST",
        "YELLOW_CARD",
        "RED_CARD",
        "SECOND_YELLOW",
        "SUBSTITUTION_IN",
        "SUBSTITUTION_OUT",
        "PENALTY_SCORED",
        "PENALTY_MISSED",
        name="event_type",
        create_type=True,
    )
    event_type_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "teams",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("short_name", sa.String(10), nullable=True),
        sa.Column("country", sa.String(100), nullable=False),
        sa.Column("founded_year", sa.Integer, nullable=True),
        sa.Column("logo_url", sa.String(500), nullable=True),
        sa.Column("stadium_name", sa.String(200), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_teams_name", "teams", ["name"], unique=True)

    op.create_table(
        "players",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "team_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("teams.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column(
            "position",
            postgresql.ENUM("GK", "DEF", "MID", "FWD", name="player_position", create_type=False),
            nullable=False,
        ),
        sa.Column("nationality", sa.String(100), nullable=True),
        sa.Column("date_of_birth", sa.Date, nullable=True),
        sa.Column("jersey_number", sa.Integer, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_players_name", "players", ["name"])
    op.create_index("ix_players_team_id", "players", ["team_id"])

    op.create_table(
        "matches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "home_team_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("teams.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "away_team_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("teams.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("kickoff_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("venue", sa.String(200), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "SCHEDULED",
                "LIVE",
                "FINISHED",
                "CANCELLED",
                "POSTPONED",
                name="match_status",
                create_type=False,
            ),
            nullable=False,
            server_default="SCHEDULED",
        ),
        sa.Column("home_score", sa.Integer, nullable=False, server_default="0"),
        sa.Column("away_score", sa.Integer, nullable=False, server_default="0"),
        sa.Column("competition", sa.String(100), nullable=True),
        sa.Column("season", sa.String(20), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_matches_home_team_id", "matches", ["home_team_id"])
    op.create_index("ix_matches_kickoff_at", "matches", ["kickoff_at"])

    op.create_table(
        "match_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "match_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("matches.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "player_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("players.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "event_type",
            postgresql.ENUM(
                "GOAL",
                "OWN_GOAL",
                "ASSIST",
                "YELLOW_CARD",
                "RED_CARD",
                "SECOND_YELLOW",
                "SUBSTITUTION_IN",
                "SUBSTITUTION_OUT",
                "PENALTY_SCORED",
                "PENALTY_MISSED",
                name="event_type",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("minute", sa.Integer, nullable=False),
        sa.Column("extra_time_minute", sa.Integer, nullable=True),
        sa.Column("meta", postgresql.JSONB, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_match_events_match_id", "match_events", ["match_id"])
    op.create_index("ix_match_events_event_type", "match_events", ["event_type"])


def downgrade() -> None:
    op.drop_table("match_events")
    op.drop_table("matches")
    op.drop_table("players")
    op.drop_table("teams")
    op.execute("DROP TYPE IF EXISTS event_type")
    op.execute("DROP TYPE IF EXISTS match_status")
    op.execute("DROP TYPE IF EXISTS player_position")
