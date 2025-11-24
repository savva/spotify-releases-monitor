from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RecentTrack(Base):
    __tablename__ = "recent_tracks"
    __table_args__ = (
        UniqueConstraint("user_id", "played_at", name="uq_recent_tracks_user_played_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(PGUUID, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    track_id: Mapped[str] = mapped_column(String(length=64), nullable=False)
    played_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    track_name: Mapped[str | None] = mapped_column(String(length=512), nullable=True)
    artist_names: Mapped[str | None] = mapped_column(String(length=512), nullable=True)
    album_name: Mapped[str | None] = mapped_column(String(length=512), nullable=True)
    raw_payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="recent_tracks")


if TYPE_CHECKING:  # pragma: no cover
    from app.models.user import User
