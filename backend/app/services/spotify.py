from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
import uuid
from typing import Any, Mapping

import httpx
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import Token, User


class SpotifyService:
    API_BASE_URL = "https://api.spotify.com/v1"
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    AUTHORIZE_URL = "https://accounts.spotify.com/authorize"

    def __init__(self, session: AsyncSession):
        self.session = session
        self.settings = get_settings()
        self._app_token: str | None = None
        self._app_token_expires_at: datetime | None = None

    async def exchange_code_for_tokens(self, code: str) -> dict[str, Any]:
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": str(self.settings.spotify_redirect_uri),
        }
        return await self._request_token(data)

    async def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        data = {"grant_type": "refresh_token", "refresh_token": refresh_token}
        return await self._request_token(data)

    async def fetch_user_profile(self, access_token: str) -> dict[str, Any]:
        return await self._api_request("GET", "/me", access_token)

    async def upsert_user_from_profile(self, profile: Mapping[str, Any]) -> User:
        stmt = select(User).where(User.spotify_user_id == profile["id"])
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if user is None:
            user = User(spotify_user_id=profile["id"])
            self.session.add(user)

        user.email = profile.get("email")
        user.display_name = profile.get("display_name")
        images = profile.get("images") or []
        user.avatar_url = images[0]["url"] if images else None
        user.country = profile.get("country")

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def upsert_user_tokens(self, user: User, token_payload: Mapping[str, Any]) -> Token:
        token = await self._get_user_token(user.id)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=token_payload.get("expires_in", 0))
        refresh_token = token_payload.get("refresh_token") or (token.refresh_token if token else None)
        if refresh_token is None:
            raise HTTPException(status_code=500, detail="Missing refresh token from Spotify response")

        if token is None:
            token = Token(
                user_id=user.id,
                access_token=token_payload["access_token"],
                refresh_token=refresh_token,
                scope=token_payload.get("scope", ""),
                token_type=token_payload.get("token_type", "Bearer"),
                expires_at=expires_at,
            )
            self.session.add(token)
            user.token = token
        else:
            token.access_token = token_payload["access_token"]
            token.refresh_token = refresh_token
            token.scope = token_payload.get("scope", token.scope)
            token.token_type = token_payload.get("token_type", token.token_type)
            token.expires_at = expires_at

        await self.session.commit()
        await self.session.refresh(token)
        return token

    async def get_recent_tracks(self, user: User) -> dict[str, Any]:
        access_token = await self._ensure_access_token(user)
        return await self._api_request(
            "GET",
            "/me/player/recently-played",
            access_token,
            params={"limit": 20},
        )

    async def add_tracks_to_playlist(self, playlist_id: str, uris: list[str], user: User) -> dict[str, Any]:
        access_token = await self._ensure_access_token(user)
        payload = {"uris": uris}
        return await self._api_request(
            "POST",
            f"/playlists/{playlist_id}/tracks",
            access_token,
            json=payload,
        )

    async def get_app_access_token(self) -> str:
        now = datetime.now(timezone.utc)
        if self._app_token and self._app_token_expires_at and self._app_token_expires_at > now + timedelta(seconds=60):
            return self._app_token

        payload = await self._request_token({"grant_type": "client_credentials"})
        access_token = payload.get("access_token")
        if not access_token:
            raise HTTPException(status_code=500, detail="Spotify token request failed")
        expires_in = payload.get("expires_in", 0)
        self._app_token = access_token
        self._app_token_expires_at = now + timedelta(seconds=expires_in)
        return access_token

    async def search_new_releases(self, *, limit: int = 50, offset: int = 0) -> dict[str, Any]:
        access_token = await self.get_app_access_token()
        safe_limit = max(1, min(limit, 50))
        safe_offset = max(0, offset)
        params = {"q": "tag:new", "type": "album", "limit": safe_limit, "offset": safe_offset}
        return await self._api_request("GET", "/search", access_token, params=params)

    async def _ensure_access_token(self, user: User) -> str:
        token = await self._get_user_token(user.id)
        if token is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Spotify tokens")

        if token.expires_at <= datetime.now(timezone.utc) + timedelta(seconds=60):
            refreshed = await self.refresh_access_token(token.refresh_token)
            await self.upsert_user_tokens(user, refreshed)
            token = await self._get_user_token(user.id)
            if token is None:
                raise HTTPException(status_code=500, detail="Unable to refresh Spotify token")
        return token.access_token

    async def _get_user_token(self, user_id: uuid.UUID) -> Token | None:
        stmt = select(Token).where(Token.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def _request_token(self, data: dict[str, Any]) -> dict[str, Any]:
        auth = (self.settings.spotify_client_id, self.settings.spotify_client_secret)
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                response = await client.post(self.TOKEN_URL, data=data, auth=auth)
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                raise HTTPException(
                    status_code=exc.response.status_code,
                    detail=f"Spotify token request failed: {exc.response.text}",
                ) from exc
            except httpx.HTTPError as exc:  # pragma: no cover - network errors
                raise HTTPException(status_code=502, detail="Unable to reach Spotify") from exc
        return response.json()

    async def _api_request(
        self,
        method: str,
        path: str,
        access_token: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        url = f"{self.API_BASE_URL}{path}"
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                response = await client.request(method, url, headers=headers, **kwargs)
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                detail = exc.response.json() if exc.response.headers.get("content-type", "").startswith("application/json") else exc.response.text
                raise HTTPException(status_code=exc.response.status_code, detail=detail)
            except httpx.HTTPError as exc:  # pragma: no cover - network errors
                raise HTTPException(status_code=502, detail="Spotify API unavailable") from exc
        return response.json()

    @staticmethod
    def build_authorize_url(state: str) -> str:
        settings = get_settings()
        scope = " ".join(settings.spotify_scopes)
        params = {
            "client_id": settings.spotify_client_id,
            "response_type": "code",
            "redirect_uri": str(settings.spotify_redirect_uri),
            "scope": scope,
            "state": state,
            "show_dialog": "false",
        }
        from urllib.parse import urlencode

        query = urlencode(params)
        return f"{SpotifyService.AUTHORIZE_URL}?{query}"

    @staticmethod
    def generate_state() -> str:
        return secrets.token_urlsafe(32)
