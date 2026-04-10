import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserUsageMonthly(Base):
    __tablename__ = 'user_usage_monthly'
    __table_args__ = (UniqueConstraint('user_id', 'period_start', name='uq_usage_user_period_start'),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), index=True)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    request_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default='0')
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default='0')
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default='0')
    total_cost_usd: Mapped[Decimal] = mapped_column(Numeric(12, 6), nullable=False, default=0, server_default='0')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    user = relationship('User', back_populates='usage_records')
