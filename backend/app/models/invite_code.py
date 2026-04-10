import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class InviteCode(Base):
    __tablename__ = 'invite_codes'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    assigned_plan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('plans.id', ondelete='RESTRICT'))
    max_uses: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default='1')
    used_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default='0')
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default='true')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    assigned_plan = relationship('Plan', back_populates='invite_codes')
