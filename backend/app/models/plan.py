import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Plan(Base):
    __tablename__ = 'plans'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    monthly_request_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    monthly_input_token_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    monthly_output_token_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    monthly_cost_limit_usd: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    allowed_models: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    max_upload_mb: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    users = relationship('User', back_populates='plan')
    invite_codes = relationship('InviteCode', back_populates='assigned_plan')
