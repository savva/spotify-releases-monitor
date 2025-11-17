from pydantic import BaseModel, Field


class PlaylistAddRequest(BaseModel):
    uris: list[str] = Field(..., min_length=1)


class PlaylistAddResponse(BaseModel):
    snapshot_id: str

    model_config = {"from_attributes": True}
