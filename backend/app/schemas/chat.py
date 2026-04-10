from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    session_id: UUID | None = None
    model: str = Field(min_length=2, max_length=128)
    message: str = Field(min_length=1, max_length=20000)


class SessionCreateRequest(BaseModel):
    title: str = Field(default='New Chat', min_length=1, max_length=255)


class ChatSessionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: str
    created_at: datetime
    updated_at: datetime


class ChatMessagePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    session_id: UUID
    role: str
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: Decimal
    created_at: datetime


class ChatSessionDetail(BaseModel):
    session: ChatSessionPublic
    messages: list[ChatMessagePublic]


class ChatResponse(BaseModel):
    session_id: UUID
    message: ChatMessagePublic


class UsageSummary(BaseModel):
    request_count: int
    input_tokens: int
    output_tokens: int
    total_cost_usd: Decimal
