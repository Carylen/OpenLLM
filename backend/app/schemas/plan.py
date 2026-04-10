from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PlanPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    monthly_request_limit: int
    monthly_input_token_limit: int
    monthly_output_token_limit: int
    monthly_cost_limit_usd: Decimal
    allowed_models: list[str]
    max_upload_mb: int
    created_at: datetime
