"""expand avatar url length

Revision ID: 20240602000000
Revises: 20240601000000
Create Date: 2024-06-02 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20240602000000"
down_revision = "20240601000000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("users", "avatar_url", type_=sa.String(length=1024))


def downgrade() -> None:
    op.alter_column("users", "avatar_url", type_=sa.String(length=512))
