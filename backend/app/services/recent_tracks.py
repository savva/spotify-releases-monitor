from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RecentTrack, User
from app.services.spotify import SpotifyService


@dataclass(slots=True)
class _ParsedTrack:
    played_at: datetime
    track_id: str
    track_name: str | None
    artist_names: str | None
    album_name: str | None
    raw_payload: dict[str, Any]


class RecentTracksSyncService:
    """Fetch and persist recently played tracks for reuse in different entry points."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.spotify = SpotifyService(session)

    async def sync(self, user: User) -> dict[str, Any]:
        payload = await self.spotify.get_recent_tracks(user)
        await self._persist_tracks(user, payload.get("items") or [])
        return payload

    async def _persist_tracks(self, user: User, items: list[dict[str, Any]]) -> None:
        parsed_tracks = []
        for item in items:
            track = item.get("track") or {}
            played_at = self._parse_played_at(item.get("played_at"))
            track_id = track.get("id")
            if played_at is None or not track_id:
                continue

            artist_names = ", ".join(
                artist.get("name")
                for artist in track.get("artists") or []
                if artist.get("name")
            )
            album = track.get("album") or {}
            parsed_tracks.append(
                _ParsedTrack(
                    played_at=played_at,
                    track_id=track_id,
                    track_name=track.get("name"),
                    artist_names=artist_names or None,
                    album_name=album.get("name"),
                    raw_payload=item,
                )
            )

        if not parsed_tracks:
            return

        played_at_values = [track.played_at for track in parsed_tracks]
        stmt = (
            select(RecentTrack.played_at)
            .where(RecentTrack.user_id == user.id)
            .where(RecentTrack.played_at.in_(played_at_values))
        )
        result = await self.session.execute(stmt)
        existing_played_at = set(result.scalars().all())

        new_records = [
            RecentTrack(
                user_id=user.id,
                track_id=track.track_id,
                played_at=track.played_at,
                track_name=track.track_name,
                artist_names=track.artist_names,
                album_name=track.album_name,
                raw_payload=track.raw_payload,
            )
            for track in parsed_tracks
            if track.played_at not in existing_played_at
        ]

        if not new_records:
            return

        self.session.add_all(new_records)
        await self.session.commit()

    @staticmethod
    def _parse_played_at(value: str | None) -> datetime | None:
        if not value:
            return None
        normalized = value.replace("Z", "+00:00") if value.endswith("Z") else value
        try:
            return datetime.fromisoformat(normalized)
        except ValueError:  # pragma: no cover - defensive guard for malformed payloads
            return None
