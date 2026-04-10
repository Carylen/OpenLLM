from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TimestampedModel(BaseModel):
    created_at: datetime


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    name: str | None
    picture_url: str | None
    is_active: bool
    is_admin: bool
