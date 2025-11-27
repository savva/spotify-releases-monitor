from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Artist, Track
from app.services.spotify import SpotifyService

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class _ParsedTrack:
    id: str
    name: str | None
    duration_ms: int | None
    track_number: int | None
    type: str | None
    popularity: int | None


@dataclass(slots=True)
class _ParsedArtist:
    id: str
    name: str | None
    type: str | None
    popularity: int | None
    followers: int | None
    genres: list[str]


class TrackArtistDetailsSyncService:
    """Fetch missing popularity/details for tracks and artists."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.spotify = SpotifyService(session)

    async def sync(self, *, batch_size: int = 50) -> tuple[int, int]:
        updated_tracks = await self.sync_tracks(batch_size=batch_size)
        updated_artists = await self.sync_artists(batch_size=batch_size)
        return updated_tracks, updated_artists

    async def sync_tracks(self, *, batch_size: int = 50) -> int:
        stmt = select(Track.id).where(Track.popularity.is_(None)).limit(batch_size)
        result = await self.session.execute(stmt)
        ids = result.scalars().all()
        if not ids:
            return 0

        payload = await self.spotify.get_tracks(ids)
        items = payload.get("tracks") or []
        parsed = self._parse_tracks(items)
        if not parsed:
            return 0

        stmt_existing = select(Track).where(Track.id.in_([track.id for track in parsed]))
        result_existing = await self.session.execute(stmt_existing)
        existing_map = {track.id: track for track in result_existing.scalars().all()}

        updated = 0
        for track in parsed:
            existing = existing_map.get(track.id)
            if not existing:
                continue
            existing.name = track.name or existing.name
            existing.duration_ms = track.duration_ms if track.duration_ms is not None else existing.duration_ms
            existing.track_number = track.track_number if track.track_number is not None else existing.track_number
            existing.type = track.type or existing.type
            if existing.popularity != track.popularity:
                existing.popularity = track.popularity
            updated += 1

        if updated:
            await self.session.commit()
        return updated

    async def sync_artists(self, *, batch_size: int = 50) -> int:
        stmt = select(Artist.id).where(Artist.popularity.is_(None)).limit(batch_size)
        result = await self.session.execute(stmt)
        ids = result.scalars().all()
        if not ids:
            return 0

        payload = await self.spotify.get_artists(ids)
        items = payload.get("artists") or []
        parsed = self._parse_artists(items)
        if not parsed:
            return 0

        stmt_existing = select(Artist).where(Artist.id.in_([artist.id for artist in parsed]))
        result_existing = await self.session.execute(stmt_existing)
        existing_map = {artist.id: artist for artist in result_existing.scalars().all()}

        updated = 0
        for artist in parsed:
            existing = existing_map.get(artist.id)
            if not existing:
                continue
            existing.name = artist.name or existing.name
            existing.type = artist.type or existing.type
            if existing.popularity != artist.popularity:
                existing.popularity = artist.popularity
            existing.followers = artist.followers if artist.followers is not None else existing.followers
            existing.genres = artist.genres or existing.genres
            updated += 1

        if updated:
            await self.session.commit()
        return updated

    def _parse_tracks(self, items: list[dict[str, Any]]) -> list[_ParsedTrack]:
        parsed = []
        for item in items:
            track_id = item.get("id")
            if not track_id:
                continue
            parsed.append(
                _ParsedTrack(
                    id=track_id,
                    name=item.get("name"),
                    duration_ms=self._parse_int(item.get("duration_ms")),
                    track_number=self._parse_int(item.get("track_number")),
                    type=item.get("type"),
                    popularity=self._parse_int(item.get("popularity")),
                )
            )
        return parsed

    def _parse_artists(self, items: list[dict[str, Any]]) -> list[_ParsedArtist]:
        parsed = []
        for item in items:
            artist_id = item.get("id")
            if not artist_id:
                continue
            followers_payload = item.get("followers") or {}
            parsed.append(
                _ParsedArtist(
                    id=artist_id,
                    name=item.get("name"),
                    type=item.get("type"),
                    popularity=self._parse_int(item.get("popularity")),
                    followers=self._parse_int(followers_payload.get("total")),
                    genres=[genre for genre in item.get("genres") or [] if isinstance(genre, str)],
                )
            )
        return parsed

    @staticmethod
    def _parse_int(value: Any) -> int | None:
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None
