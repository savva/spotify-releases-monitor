from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Release(Base):
    __tablename__ = "releases"

    id: Mapped[str] = mapped_column(String(length=64), primary_key=True)
    name: Mapped[str] = mapped_column(String(length=512), nullable=False)
    release_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    total_tracks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    popularity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), server_default=func.now()
    )
