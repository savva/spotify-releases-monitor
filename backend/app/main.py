from contextlib import asynccontextmanager
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import get_settings
from app.tasks import (
    sync_new_releases,
    sync_recent_release_details,
    sync_recent_tracks_for_all_users,
    sync_track_details,
    sync_artist_details,
)

settings = get_settings()
scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(_: FastAPI):
    if not scheduler.running:
        scheduler.add_job(
            sync_recent_tracks_for_all_users,
            trigger=IntervalTrigger(minutes=5),
            id="sync_recent_tracks",
            replace_existing=True,
        )
        scheduler.add_job(
            sync_new_releases,
            trigger=IntervalTrigger(minutes=15),
            id="sync_new_releases",
            replace_existing=True,
        )
        scheduler.add_job(
            sync_recent_release_details,
            trigger=IntervalTrigger(minutes=10),
            id="sync_recent_release_details",
            replace_existing=True,
        )
        scheduler.add_job(
            sync_track_details,
            trigger=IntervalTrigger(minutes=6),
            id="sync_track_details",
            replace_existing=True,
        )
        scheduler.add_job(
            sync_artist_details,
            trigger=IntervalTrigger(minutes=12),
            id="sync_artist_details",
            replace_existing=True,
        )
        scheduler.start()
    try:
        yield
    finally:
        if scheduler.running:
            scheduler.shutdown(wait=False)


app = FastAPI(title=settings.app_name, lifespan=lifespan)

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

app.include_router(api_router)

static_dir = Path(__file__).parent / "static"
assets_dir = static_dir / "assets"

if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


@app.get("/", include_in_schema=False)
async def serve_index() -> FileResponse:
    index_path = static_dir / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend not built yet")
    return FileResponse(index_path)


@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str) -> FileResponse:
    requested_path = static_dir / full_path
    if requested_path.is_file():
        return FileResponse(requested_path)
    index_path = static_dir / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend not built yet")
    return FileResponse(index_path)
