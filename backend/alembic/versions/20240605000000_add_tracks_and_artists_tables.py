"""add track and artist tables

Revision ID: 20240605000000
Revises: 20240604000000
Create Date: 2024-06-05 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20240605000000"
down_revision = "20240604000000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "artists",
        sa.Column("id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=512), nullable=True),
        sa.Column("type", sa.String(length=64), nullable=True),
        sa.Column("popularity", sa.Integer(), nullable=True),
        sa.Column("followers", sa.Integer(), nullable=True),
        sa.Column("genres", postgresql.ARRAY(sa.String(length=128)), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "tracks",
        sa.Column("id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=512), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("track_number", sa.Integer(), nullable=True),
        sa.Column("type", sa.String(length=64), nullable=True),
        sa.Column("popularity", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "release_tracks",
        sa.Column("release_id", sa.String(length=64), nullable=False),
        sa.Column("track_id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["release_id"], ["releases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["track_id"], ["tracks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("release_id", "track_id"),
    )
    op.create_index("ix_release_tracks_release_id", "release_tracks", ["release_id"])
    op.create_index("ix_release_tracks_track_id", "release_tracks", ["track_id"])

    op.create_table(
        "track_artists",
        sa.Column("track_id", sa.String(length=64), nullable=False),
        sa.Column("artist_id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["artist_id"], ["artists.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["track_id"], ["tracks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("track_id", "artist_id"),
    )
    op.create_index("ix_track_artists_track_id", "track_artists", ["track_id"])
    op.create_index("ix_track_artists_artist_id", "track_artists", ["artist_id"])


def downgrade() -> None:
    op.drop_index("ix_track_artists_artist_id", table_name="track_artists")
    op.drop_index("ix_track_artists_track_id", table_name="track_artists")
    op.drop_table("track_artists")

    op.drop_index("ix_release_tracks_track_id", table_name="release_tracks")
    op.drop_index("ix_release_tracks_release_id", table_name="release_tracks")
    op.drop_table("release_tracks")

    op.drop_table("tracks")
    op.drop_table("artists")
