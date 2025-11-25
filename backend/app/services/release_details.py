from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import logging
from typing import Any
from urllib.parse import parse_qs, urlparse

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Artist, Release, ReleaseTrack, Track, TrackArtist
from app.services.spotify import SpotifyService

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class _ParsedTrack:
    id: str
    name: str | None
    duration_ms: int | None
    track_number: int | None
    type: str | None
    artist_ids: list[str]


@dataclass(slots=True)
class _ParsedArtist:
    id: str
    name: str | None
    type: str | None
    popularity: int | None
    followers: int | None
    genres: list[str]


class ReleaseDetailsSyncService:
    """Fetch album details (tracks and artists) for recent releases missing metadata."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.spotify = SpotifyService(session)

    async def sync_recent_releases(self, *, days: int = 30) -> int:
        release_ids = await self._get_releases_needing_details(days)
        if not release_ids:
            return 0

        processed = 0
        for release_id in release_ids:
            try:
                album = await self._fetch_full_album(release_id)
            except Exception as exc:  # pragma: no cover - background logging only
                logger.warning("Failed to fetch album %s details: %s", release_id, exc)
                continue

            if not album:
                continue

            await self._persist_album(album)
            processed += 1

        return processed

    async def _get_releases_needing_details(self, days: int) -> list[str]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = (
            select(Release.id)
            .where(Release.created_at >= cutoff)
            .where(~exists().where(ReleaseTrack.release_id == Release.id))
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def _fetch_full_album(self, release_id: str) -> dict[str, Any]:
        album = await self.spotify.get_album(release_id)
        if not album:
            return {}

        tracks_payload = album.get("tracks") or {}
        items = list(tracks_payload.get("items") or [])
        next_url = tracks_payload.get("next")
        current_offset = tracks_payload.get("offset") or 0
        current_limit = tracks_payload.get("limit") or len(items) or 50

        while next_url:
            next_offset, next_limit = self._parse_next_page(
                next_url,
                fallback_offset=current_offset + current_limit,
                fallback_limit=current_limit,
            )
            if next_offset <= current_offset:
                break

            page = await self.spotify.get_album_tracks(release_id, limit=next_limit, offset=next_offset)
            page_items = page.get("items") or []
            items.extend(page_items)
            current_offset = page.get("offset") or next_offset
            current_limit = page.get("limit") or next_limit
            next_url = page.get("next")

        album["tracks"] = {
            **tracks_payload,
            "items": items,
            "offset": current_offset,
            "limit": current_limit,
            "next": next_url,
        }
        return album

    async def _persist_album(self, album: dict[str, Any]) -> None:
        release_id = album.get("id")
        if not release_id:
            return

        release = await self.session.get(Release, release_id)
        if not release:
            return

        release.popularity = self._parse_int(album.get("popularity"))
        parsed_total_tracks = self._parse_int(album.get("total_tracks"))
        if parsed_total_tracks is not None:
            release.total_tracks = parsed_total_tracks
        self.session.add(release)

        tracks_payload = album.get("tracks") or {}
        track_items = tracks_payload.get("items") or []
        parsed_tracks = self._parse_tracks(track_items)
        parsed_artists = self._parse_artists(album, track_items)

        await self._upsert_tracks(parsed_tracks)
        await self._upsert_artists(parsed_artists)
        await self._upsert_release_tracks(release_id, parsed_tracks)
        await self._upsert_track_artists(parsed_tracks)

        await self.session.commit()

    async def _upsert_tracks(self, parsed_tracks: list[_ParsedTrack]) -> None:
        if not parsed_tracks:
            return

        track_ids = [track.id for track in parsed_tracks]
        stmt = select(Track).where(Track.id.in_(track_ids))
        result = await self.session.execute(stmt)
        existing_tracks = {track.id: track for track in result.scalars().all()}

        new_tracks: list[Track] = []
        for track in parsed_tracks:
            existing = existing_tracks.get(track.id)
            if existing:
                existing.name = track.name or existing.name
                existing.duration_ms = track.duration_ms if track.duration_ms is not None else existing.duration_ms
                existing.track_number = track.track_number if track.track_number is not None else existing.track_number
                existing.type = track.type or existing.type
            else:
                new_tracks.append(
                    Track(
                        id=track.id,
                        name=track.name,
                        duration_ms=track.duration_ms,
                        track_number=track.track_number,
                        type=track.type,
                    )
                )

        if new_tracks:
            self.session.add_all(new_tracks)

    async def _upsert_artists(self, parsed_artists: list[_ParsedArtist]) -> None:
        if not parsed_artists:
            return

        artist_ids = [artist.id for artist in parsed_artists]
        stmt = select(Artist).where(Artist.id.in_(artist_ids))
        result = await self.session.execute(stmt)
        existing_artists = {artist.id: artist for artist in result.scalars().all()}

        new_artists: list[Artist] = []
        for artist in parsed_artists:
            existing = existing_artists.get(artist.id)
            if existing:
                existing.name = artist.name or existing.name
                existing.type = artist.type or existing.type
                existing.popularity = artist.popularity if artist.popularity is not None else existing.popularity
                existing.followers = artist.followers if artist.followers is not None else existing.followers
                existing.genres = artist.genres or existing.genres
            else:
                new_artists.append(
                    Artist(
                        id=artist.id,
                        name=artist.name,
                        type=artist.type,
                        popularity=artist.popularity,
                        followers=artist.followers,
                        genres=artist.genres or None,
                    )
                )

        if new_artists:
            self.session.add_all(new_artists)

    async def _upsert_release_tracks(self, release_id: str, parsed_tracks: list[_ParsedTrack]) -> None:
        if not parsed_tracks:
            return

        track_ids = [track.id for track in parsed_tracks]
        stmt = (
            select(ReleaseTrack.track_id)
            .where(ReleaseTrack.release_id == release_id)
            .where(ReleaseTrack.track_id.in_(track_ids))
        )
        result = await self.session.execute(stmt)
        existing = set(result.scalars().all())

        new_links = [
            ReleaseTrack(release_id=release_id, track_id=track_id)
            for track_id in track_ids
            if track_id not in existing
        ]
        if new_links:
            self.session.add_all(new_links)

    async def _upsert_track_artists(self, parsed_tracks: list[_ParsedTrack]) -> None:
        if not parsed_tracks:
            return

        pairs = {(track.id, artist_id) for track in parsed_tracks for artist_id in track.artist_ids}
        if not pairs:
            return

        track_ids = list({track_id for track_id, _ in pairs})
        artist_ids = list({artist_id for _, artist_id in pairs})

        stmt = (
            select(TrackArtist.track_id, TrackArtist.artist_id)
            .where(TrackArtist.track_id.in_(track_ids))
            .where(TrackArtist.artist_id.in_(artist_ids))
        )
        result = await self.session.execute(stmt)
        existing_pairs = {(row[0], row[1]) for row in result.all()}

        new_links = [
            TrackArtist(track_id=track_id, artist_id=artist_id)
            for track_id, artist_id in pairs
            if (track_id, artist_id) not in existing_pairs
        ]
        if new_links:
            self.session.add_all(new_links)

    def _parse_tracks(self, items: list[dict[str, Any]]) -> list[_ParsedTrack]:
        parsed = []
        for item in items:
            track_id = item.get("id")
            if not track_id:
                continue
            artist_ids = [artist.get("id") for artist in item.get("artists") or [] if artist.get("id")]
            parsed.append(
                _ParsedTrack(
                    id=track_id,
                    name=item.get("name"),
                    duration_ms=self._parse_int(item.get("duration_ms")),
                    track_number=self._parse_int(item.get("track_number")),
                    type=item.get("type"),
                    artist_ids=artist_ids,
                )
            )
        return parsed

    def _parse_artists(self, album: dict[str, Any], tracks: list[dict[str, Any]]) -> list[_ParsedArtist]:
        artists: dict[str, _ParsedArtist] = {}

        def add_artist(payload: dict[str, Any]) -> None:
            artist_id = payload.get("id")
            if not artist_id:
                return
            if artist_id in artists:
                return
            artists[artist_id] = _ParsedArtist(
                id=artist_id,
                name=payload.get("name"),
                type=payload.get("type"),
                popularity=self._parse_int(payload.get("popularity")),
                followers=self._parse_int((payload.get("followers") or {}).get("total")),
                genres=[genre for genre in payload.get("genres") or [] if isinstance(genre, str)],
            )

        for artist in album.get("artists") or []:
            add_artist(artist)

        for track in tracks:
            for artist in track.get("artists") or []:
                add_artist(artist)

        return list(artists.values())

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

    @staticmethod
    def _parse_int(value: Any) -> int | None:
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None
