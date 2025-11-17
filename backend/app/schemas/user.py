import uuid
from datetime import datetime

from pydantic import BaseModel


class UserOut(BaseModel):
    id: uuid.UUID
    spotify_user_id: str
    email: str | None
    display_name: str | None
    avatar_url: str | None
    country: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
