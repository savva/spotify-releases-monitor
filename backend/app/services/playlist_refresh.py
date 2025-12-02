from __future__ import annotations

from dataclasses import dataclass
import logging
import re
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RecentTrack, Track, User
from app.services.recent_tracks import RecentTracksSyncService
from app.services.spotify import SpotifyService

logger = logging.getLogger(__name__)

PLAYLIST_ID_RE = re.compile(
    r"(?:spotify:playlist:|https?://open\.spotify\.com/playlist/)?(?P<id>[A-Za-z0-9]+)"
)


@dataclass(slots=True)
class _PlaylistTrack:
    track_id: str | None
    name: str | None
    artists: list[str]
    album: str | None
    uri: str | None
    popularity: int | None


class PlaylistRefreshService:
    """Preview and refresh playlist content based on listening history."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.spotify = SpotifyService(session)

    async def preview_playlist(self, playlist_url: str, user: User) -> dict[str, Any]:
        playlist_id = self._parse_playlist_id(playlist_url)
        playlist, tracks = await self._fetch_playlist_with_tracks(playlist_id, user)
        return self._build_response(playlist_id, playlist, tracks, removed=0, added=0)

    async def refresh_playlist(self, playlist_url: str, user: User, *, target_size: int = 20) -> dict[str, Any]:
        playlist_id = self._parse_playlist_id(playlist_url)

        # Refresh recent listening from Spotify, then rely on stored data
        await RecentTracksSyncService(self.session).sync(user)
        listened_ids = await self._get_listened_track_ids(user)
        logger.info(
            f"Starting playlist refresh - playlist_id={playlist_id}, listened_count={len(listened_ids)}, target_size={target_size}"
        )

        playlist, tracks = await self._fetch_playlist_with_tracks(playlist_id, user)

        to_remove = [
            track.uri for track in tracks if track.track_id and track.track_id in listened_ids and track.uri
        ]

        logger.info(
            f'Listened track IDs: {listened_ids}'
        )
        logger.info(
            f'Current playlist tracks: {[track.track_id for track in tracks]}'
        )


        logger.info(
            f"Computed tracks to remove - playlist_id={playlist_id}, current_track_count={len(tracks)}, to_remove_count={len(to_remove)}"
        )
        removed = 0
        if to_remove:
            await self.spotify.remove_tracks_from_playlist(playlist_id, to_remove, user)
            removed = len(to_remove)
            logger.info(
                f"Removed listened tracks from playlist - playlist_id={playlist_id}, removed={removed}"
            )

        # Re-fetch after removals
        playlist, tracks = await self._fetch_playlist_with_tracks(playlist_id, user)
        current_ids = {track.track_id for track in tracks if track.track_id}

        needed = max(0, target_size - len(current_ids))
        added = 0
        logger.info(
            f"Post-removal playlist state - playlist_id={playlist_id}, current_track_count={len(current_ids)}, needed={needed}, target_size={target_size}"
        )
        if needed:
            candidates = await self._get_candidate_tracks(exclude_ids=current_ids | listened_ids, limit=needed)
            if candidates:
                uris = [f"spotify:track:{track_id}" for track_id in candidates]
                await self.spotify.add_tracks_to_playlist(playlist_id, uris, user)
                added = len(uris)
                logger.info(
                    f"Added candidate tracks to playlist - playlist_id={playlist_id}, added={added}, candidate_pool={len(candidates)}"
                )
                playlist, tracks = await self._fetch_playlist_with_tracks(playlist_id, user)

        return self._build_response(playlist_id, playlist, tracks, removed=removed, added=added)

    async def _fetch_playlist_with_tracks(self, playlist_id: str, user: User) -> tuple[dict[str, Any], list[_PlaylistTrack]]:
        playlist = await self.spotify.get_playlist(playlist_id, user)
        tracks = await self._collect_playlist_tracks(playlist_id, user, playlist.get("tracks") or {})
        return playlist, tracks

    async def _collect_playlist_tracks(
        self,
        playlist_id: str,
        user: User,
        initial_payload: dict[str, Any],
    ) -> list[_PlaylistTrack]:
        items = list(initial_payload.get("items") or [])
        next_url = initial_payload.get("next")
        offset = initial_payload.get("offset") or 0
        limit = initial_payload.get("limit") or len(items) or 100

        while next_url:
            # Spotify playlist next url always includes offset/limit
            offset += limit
            page = await self.spotify.get_playlist_tracks(playlist_id, user, limit=limit, offset=offset)
            items.extend(page.get("items") or [])
            limit = page.get("limit") or limit
            next_url = page.get("next")

        parsed = []
        for item in items:
            track = item.get("track") or {}
            parsed.append(
                _PlaylistTrack(
                    track_id=track.get("id"),
                    name=track.get("name"),
                    artists=[artist.get("name") for artist in track.get("artists") or [] if artist.get("name")],
                    album=(track.get("album") or {}).get("name"),
                    uri=track.get("uri"),
                    popularity=self._parse_int(track.get("popularity")),
                )
            )
        return parsed

    async def _get_listened_track_ids(self, user: User) -> set[str]:
        stmt = select(RecentTrack.track_id).where(RecentTrack.user_id == user.id)
        result = await self.session.execute(stmt)
        return set(result.scalars().all())

    async def _get_candidate_tracks(self, *, exclude_ids: set[str], limit: int) -> list[str]:
        stmt = select(Track.id).where(Track.popularity.is_not(None))
        if exclude_ids:
            stmt = stmt.where(~Track.id.in_(exclude_ids))
        stmt = stmt.order_by(Track.popularity.desc()).limit(limit * 3)  # grab extras in case some are missing
        result = await self.session.execute(stmt)
        ids = [row for row in result.scalars().all()]
        # Keep order, enforce uniqueness, trim to requested limit
        seen: set[str] = set()
        deduped: list[str] = []
        for track_id in ids:
            if track_id in seen:
                continue
            seen.add(track_id)
            deduped.append(track_id)
            if len(deduped) >= limit:
                break
        return deduped

    @staticmethod
    def _parse_playlist_id(value: str) -> str:
        match = PLAYLIST_ID_RE.search(value.strip())
        if not match:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid playlist link or ID",
            )
        return match.group("id")

    @staticmethod
    def _build_response(
        playlist_id: str,
        playlist: dict[str, Any],
        tracks: list[_PlaylistTrack],
        *,
        removed: int,
        added: int,
    ) -> dict[str, Any]:
        return {
            "playlist_id": playlist_id,
            "name": playlist.get("name"),
            "tracks": [
                {
                    "id": track.track_id,
                    "name": track.name,
                    "artists": track.artists,
                    "album": track.album,
                    "uri": track.uri,
                    "popularity": track.popularity,
                }
                for track in tracks
                if track.track_id
            ],
            "removed": removed,
            "added": added,
        }

    @staticmethod
    def _parse_int(value: Any) -> int | None:
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None
