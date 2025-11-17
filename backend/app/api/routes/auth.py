from fastapi import APIRouter, Cookie, Depends, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.core.security import (
    STATE_COOKIE_NAME,
    clear_session_cookie,
    clear_state_cookie,
    create_access_token,
    set_session_cookie,
    set_state_cookie,
)
from app.db.session import get_session
from app.models import User
from app.services.spotify import SpotifyService

router = APIRouter()


@router.get("/login", status_code=302)
async def login() -> RedirectResponse:
    state = SpotifyService.generate_state()
    authorize_url = SpotifyService.build_authorize_url(state)
    response = RedirectResponse(url=authorize_url, status_code=302)
    set_state_cookie(response, state)
    return response


@router.get("/callback")
async def callback(
    code: str,
    state: str,
    session: AsyncSession = Depends(get_session),
    stored_state: str | None = Cookie(default=None, alias=STATE_COOKIE_NAME),
) -> RedirectResponse:
    settings = get_settings()
    if not stored_state or stored_state != state:
        raise HTTPException(status_code=400, detail="Invalid Spotify state parameter")

    spotify = SpotifyService(session)
    token_payload = await spotify.exchange_code_for_tokens(code)
    profile = await spotify.fetch_user_profile(token_payload["access_token"])
    user = await spotify.upsert_user_from_profile(profile)
    await spotify.upsert_user_tokens(user, token_payload)

    jwt_token = create_access_token(user.id)
    response = RedirectResponse(url=settings.app_url, status_code=303)
    set_session_cookie(response, jwt_token)
    clear_state_cookie(response)
    return response


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)) -> JSONResponse:
    _ = current_user
    response = JSONResponse({"detail": "Logged out"})
    clear_session_cookie(response)
    return response
