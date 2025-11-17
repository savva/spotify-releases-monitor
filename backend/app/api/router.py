from fastapi import APIRouter

from app.api.routes import auth, spotify, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(spotify.router, prefix="/spotify", tags=["spotify"])
