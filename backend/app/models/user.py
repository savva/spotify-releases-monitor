from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID, primary_key=True, default=uuid.uuid4)
    spotify_user_id: Mapped[str] = mapped_column(String(length=255), unique=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(length=255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(length=1024), nullable=True)
    country: Mapped[str | None] = mapped_column(String(length=2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now(),
        server_default=func.now(),
    )

    token: Mapped["Token | None"] = relationship(
        "Token", back_populates="user", cascade="all, delete-orphan", uselist=False
    )


if TYPE_CHECKING:  # pragma: no cover
    from app.models.token import Token
