"""add recent tracks table

Revision ID: 20240603000000
Revises: 20240602000000
Create Date: 2024-06-03 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20240603000000"
down_revision = "20240602000000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "recent_tracks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("track_id", sa.String(length=64), nullable=False),
        sa.Column("played_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("track_name", sa.String(length=512), nullable=True),
        sa.Column("artist_names", sa.String(length=512), nullable=True),
        sa.Column("album_name", sa.String(length=512), nullable=True),
        sa.Column(
            "raw_payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "played_at", name="uq_recent_tracks_user_played_at"),
    )
    op.create_index(
        "ix_recent_tracks_user_played_at",
        "recent_tracks",
        ["user_id", "played_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_recent_tracks_user_played_at", table_name="recent_tracks")
    op.drop_table("recent_tracks")
