from __future__ import annotations

import logging

from app.db.session import AsyncSessionLocal
from app.services.new_releases import NewReleasesSyncService

logger = logging.getLogger(__name__)


async def sync_new_releases() -> None:
    async with AsyncSessionLocal() as session:
        service = NewReleasesSyncService(session)
        try:
            created = await service.sync()
            logger.info("Synced %d new releases", created)
        except Exception as exc:  # pragma: no cover - background logging only
            logger.warning("Failed to sync new releases: %s", exc)
