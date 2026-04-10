from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UsageMonthlyPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    period_start: date
    period_end: date
    request_count: int
    input_tokens: int
    output_tokens: int
    total_cost_usd: Decimal
    created_at: datetime
    updated_at: datetime
