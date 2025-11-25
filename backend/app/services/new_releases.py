from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import logging
from typing import Any
from urllib.parse import parse_qs, urlparse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Release
from app.services.spotify import SpotifyService

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class _ParsedRelease:
    id: str
    name: str
    release_date: date | None
    total_tracks: int | None
    popularity: int | None


class NewReleasesSyncService:
    """Fetch and persist new releases returned by Spotify's tag:new search."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.spotify = SpotifyService(session)

    async def sync(self, *, limit: int = 50, max_offset: int = 1000) -> int:
        albums = await self._fetch_new_releases(limit=limit, max_offset=max_offset)
        parsed = self._parse_albums(albums)
        return await self._persist(parsed)

    async def _fetch_new_releases(self, *, limit: int, max_offset: int) -> list[dict[str, Any]]:
        offset = 0
        request_limit = limit
        albums: list[dict[str, Any]] = []
        page = 0
        while offset < max_offset:
            page += 1
            logger.info("Fetching new releases page %d (offset=%d, limit=%d)", page, offset, request_limit)
            payload = await self.spotify.search_new_releases(limit=request_limit, offset=offset)
            album_payload = payload.get("albums") or {}
            items = album_payload.get("items") or []
            if not items:
                break

            albums.extend(items)

            next_offset, next_limit = self._parse_next_page(
                album_payload.get("next"),
                fallback_offset=offset + (album_payload.get("limit") or request_limit),
                fallback_limit=request_limit,
            )
            if next_offset >= max_offset:
                break
            if next_offset <= offset:
                break
            offset = next_offset
            request_limit = next_limit
        return albums

    def _parse_albums(self, albums: list[dict[str, Any]]) -> list[_ParsedRelease]:
        parsed: dict[str, _ParsedRelease] = {}
        for album in albums:
            album_id = album.get("id")
            name = album.get("name")
            if not album_id or not name:
                continue

            parsed[album_id] = _ParsedRelease(
                id=album_id,
                name=name,
                release_date=self._parse_release_date(album.get("release_date")),
                total_tracks=self._parse_int(album.get("total_tracks")),
                popularity=self._parse_int(album.get("popularity")),
            )
        return list(parsed.values())

    async def _persist(self, releases: list[_ParsedRelease]) -> int:
        if not releases:
            return 0

        ids = [release.id for release in releases]
        stmt = select(Release.id).where(Release.id.in_(ids))
        result = await self.session.execute(stmt)
        existing_ids = set(result.scalars().all())

        new_records = [
            Release(
                id=release.id,
                name=release.name,
                release_date=release.release_date,
                total_tracks=release.total_tracks,
                popularity=release.popularity,
            )
            for release in releases
            if release.id not in existing_ids
        ]

        if not new_records:
            return 0

        self.session.add_all(new_records)
        await self.session.commit()
        return len(new_records)

    @staticmethod
    def _parse_release_date(value: str | None) -> date | None:
        if not value:
            return None
        for candidate in (value, f"{value}-01", f"{value}-01-01"):
            try:
                return date.fromisoformat(candidate)
            except ValueError:
                continue
        return None

    @staticmethod
    def _parse_int(value: Any) -> int | None:
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _parse_next_page(next_url: str | None, *, fallback_offset: int, fallback_limit: int) -> tuple[int, int]:
        if not next_url:
            return fallback_offset, fallback_limit

        try:
            parsed = urlparse(next_url)
            query = parse_qs(parsed.query)
            next_offset = int(query.get("offset", [fallback_offset])[0])
            next_limit = int(query.get("limit", [fallback_limit])[0])
        except (ValueError, TypeError, IndexError):
            return fallback_offset, fallback_limit

        return max(0, next_offset), max(1, min(next_limit, 50))
