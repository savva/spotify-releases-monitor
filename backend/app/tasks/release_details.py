from __future__ import annotations

import logging

from app.db.session import AsyncSessionLocal
from app.services.release_details import ReleaseDetailsSyncService

logger = logging.getLogger(__name__)


async def sync_recent_release_details() -> None:
    async with AsyncSessionLocal() as session:
        service = ReleaseDetailsSyncService(session)
        try:
            synced = await service.sync_recent_releases()
            logger.info("Synced details for %d releases", synced)
        except Exception as exc:  # pragma: no cover - background logging only
            logger.warning("Failed to sync release details: %s", exc)
