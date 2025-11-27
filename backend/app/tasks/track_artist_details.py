from __future__ import annotations

import logging

from app.db.session import AsyncSessionLocal
from app.services.track_artist_details import TrackArtistDetailsSyncService

logger = logging.getLogger(__name__)


async def sync_track_details() -> None:
    async with AsyncSessionLocal() as session:
        service = TrackArtistDetailsSyncService(session)
        try:
            tracks_updated = await service.sync_tracks()
            logger.info("Synced popularity for %d tracks", tracks_updated)
        except Exception as exc:  # pragma: no cover - background logging only
            logger.warning("Failed to sync track details: %s", exc)


async def sync_artist_details() -> None:
    async with AsyncSessionLocal() as session:
        service = TrackArtistDetailsSyncService(session)
        try:
            artists_updated = await service.sync_artists()
            logger.info("Synced popularity for %d artists", artists_updated)
        except Exception as exc:  # pragma: no cover - background logging only
            logger.warning("Failed to sync artist details: %s", exc)
