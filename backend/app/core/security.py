from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from uuid import UUID

import jwt
from fastapi import Response

from app.core.config import get_settings

SESSION_COOKIE_NAME = "srm_session"
STATE_COOKIE_NAME = "srm_state"


def create_access_token(subject: UUID, extra: Dict[str, Any] | None = None) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_ttl_min)
    payload: Dict[str, Any] = {"sub": str(subject), "exp": expire}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_alg)


def decode_access_token(token: str) -> Dict[str, Any]:
    settings = get_settings()
    return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_alg])


def set_session_cookie(response: Response, token: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        max_age=settings.jwt_ttl_min * 60,
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/")


def set_state_cookie(response: Response, state: str) -> None:
    settings = get_settings()
    response.set_cookie(
        key=STATE_COOKIE_NAME,
        value=state,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        max_age=600,
        path="/",
    )


def clear_state_cookie(response: Response) -> None:
    response.delete_cookie(key=STATE_COOKIE_NAME, path="/")
