"""add releases table

Revision ID: 20240604000000
Revises: 20240603000000
Create Date: 2024-06-04 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20240604000000"
down_revision = "20240603000000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "releases",
        sa.Column("id", sa.String(length=64), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=512), nullable=False),
        sa.Column("release_date", sa.Date(), nullable=True),
        sa.Column("total_tracks", sa.Integer(), nullable=True),
        sa.Column("popularity", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_releases_release_date", "releases", ["release_date"])


def downgrade() -> None:
    op.drop_index("ix_releases_release_date", table_name="releases")
    op.drop_table("releases")
