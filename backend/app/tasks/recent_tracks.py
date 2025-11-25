from __future__ import annotations

import logging

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models import User
from app.services.recent_tracks import RecentTracksSyncService

logger = logging.getLogger(__name__)


async def sync_recent_tracks_for_all_users() -> None:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        if not users:
            logger.info("No users found for recent track sync")
            return

        logger.info("Starting recent track sync for %d users", len(users))
        sync_service = RecentTracksSyncService(session)
        for user in users:
            try:
                await sync_service.sync(user)
                logger.info("Synced recent tracks for user %s", user.id)
            except Exception as exc:  # pragma: no cover - background logging only
                logger.warning("Failed to sync recent tracks for user %s: %s", user.id, exc)
