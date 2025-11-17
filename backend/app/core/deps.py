import uuid

from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import SESSION_COOKIE_NAME, decode_access_token
from app.db.session import get_session
from app.models import User


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    token: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME),
) -> User:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    try:
        payload = decode_access_token(token)
        subject = payload.get("sub")
        user_id = uuid.UUID(subject)
    except Exception as exc:  # pragma: no cover - token errors
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    stmt = select(User).options(selectinload(User.token)).where(User.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user
