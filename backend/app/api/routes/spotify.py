from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_session
from app.models import User
from app.schemas.spotify import PlaylistAddRequest, PlaylistAddResponse
from app.services.recent_tracks import RecentTracksSyncService
from app.services.spotify import SpotifyService

router = APIRouter()


@router.get("/recent")
async def recent_tracks(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    return await RecentTracksSyncService(session).sync(current_user)


@router.post("/playlists/{playlist_id}/add", response_model=PlaylistAddResponse)
async def add_tracks(
    playlist_id: str,
    payload: PlaylistAddRequest,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> PlaylistAddResponse:
    spotify = SpotifyService(session)
    result = await spotify.add_tracks_to_playlist(playlist_id, payload.uris, current_user)
    return PlaylistAddResponse.model_validate(result)
