"""video_uploads table

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    upload_status_enum = postgresql.ENUM(
        "PENDING",
        "PROCESSING",
        "READY",
        "FAILED",
        name="upload_status",
        create_type=True,
    )
    upload_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "video_uploads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "match_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("matches.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "uploaded_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("storage_key", sa.String(500), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger, nullable=False),
        sa.Column("content_type", sa.String(100), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "PENDING",
                "PROCESSING",
                "READY",
                "FAILED",
                name="upload_status",
                create_type=False,
            ),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("duration_seconds", sa.Float, nullable=True),
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
    op.create_index("ix_video_uploads_match_id", "video_uploads", ["match_id"])
    op.create_index("ix_video_uploads_uploaded_by", "video_uploads", ["uploaded_by"])
    op.create_index("ix_video_uploads_storage_key", "video_uploads", ["storage_key"], unique=True)


def downgrade() -> None:
    op.drop_table("video_uploads")
    op.execute("DROP TYPE IF EXISTS upload_status")
