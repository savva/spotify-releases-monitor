from pydantic import BaseModel, Field


class PlaylistAddRequest(BaseModel):
    uris: list[str] = Field(..., min_length=1)


class PlaylistAddResponse(BaseModel):
    snapshot_id: str

    model_config = {"from_attributes": True}


class PlaylistLinkRequest(BaseModel):
    playlist_url: str = Field(..., description="Full playlist URL or playlist ID")


class PlaylistTrack(BaseModel):
    id: str
    name: str | None = None
    artists: list[str] = Field(default_factory=list)
    album: str | None = None
    uri: str | None = None
    popularity: int | None = None


class PlaylistPreviewResponse(BaseModel):
    playlist_id: str
    name: str | None = None
    tracks: list[PlaylistTrack] = Field(default_factory=list)
    removed: int = 0
    added: int = 0
