from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Token(Base):
    __tablename__ = "tokens"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID, ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    access_token: Mapped[str] = mapped_column(String(length=512), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(length=512), nullable=False)
    scope: Mapped[str] = mapped_column(String(length=512), nullable=False)
    token_type: Mapped[str] = mapped_column(String(length=64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="token")


if TYPE_CHECKING:  # pragma: no cover
    from app.models.user import User
