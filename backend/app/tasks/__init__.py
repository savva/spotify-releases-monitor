from app.tasks.new_releases import sync_new_releases
from app.tasks.release_details import sync_recent_release_details
from app.tasks.recent_tracks import sync_recent_tracks_for_all_users
from app.tasks.track_artist_details import sync_artist_details, sync_track_details

__all__ = [
    "sync_recent_tracks_for_all_users",
    "sync_new_releases",
    "sync_recent_release_details",
    "sync_track_details",
    "sync_artist_details",
]
