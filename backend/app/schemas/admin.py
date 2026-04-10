from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AdminUserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    name: str | None
    is_active: bool
    plan_id: UUID | None
    created_at: datetime


class AssignPlanRequest(BaseModel):
    plan_code: str = Field(min_length=2, max_length=64)


class AdminPlanPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str


class InviteCodeCreateRequest(BaseModel):
    code: str | None = Field(default=None, min_length=3, max_length=128)
    assigned_plan_code: str = Field(min_length=2, max_length=64)
    max_uses: int = Field(default=1, ge=1, le=10000)
    expires_at: datetime | None = None


class AdminInviteCodePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    created_by: UUID | None
    assigned_plan_id: UUID
    max_uses: int
    used_count: int
    expires_at: datetime | None
    is_active: bool
    created_at: datetime
