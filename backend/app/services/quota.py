from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.plan import Plan
from app.models.user import User
from app.models.user_usage_monthly import UserUsageMonthly
from app.utils.usage import get_month_period


def get_or_create_current_usage(db: Session, user: User) -> UserUsageMonthly:
    period_start, period_end = get_month_period(date.today())
    usage = db.scalar(
        select(UserUsageMonthly).where(
            UserUsageMonthly.user_id == user.id,
            UserUsageMonthly.period_start == period_start,
        )
    )
    if usage:
        return usage

    usage = UserUsageMonthly(user_id=user.id, period_start=period_start, period_end=period_end)
    db.add(usage)
    db.commit()
    db.refresh(usage)
    return usage


def ensure_plan_and_model_allowed(user: User, model: str) -> Plan:
    if not user.plan:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='No plan assigned')
    if model not in user.plan.allowed_models:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Model not allowed for current plan')
    return user.plan


def enforce_quota_before_request(usage: UserUsageMonthly, plan: Plan) -> None:
    if usage.request_count + 1 > plan.monthly_request_limit:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Monthly request quota exceeded')
    if usage.input_tokens >= plan.monthly_input_token_limit:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Monthly input token quota exceeded')
    if usage.output_tokens >= plan.monthly_output_token_limit:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Monthly output token quota exceeded')
    if Decimal(usage.total_cost_usd) >= Decimal(plan.monthly_cost_limit_usd):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Monthly cost quota exceeded')


def apply_usage_increment(
    usage: UserUsageMonthly,
    *,
    input_tokens: int,
    output_tokens: int,
    cost_usd: Decimal,
) -> None:
    usage.request_count += 1
    usage.input_tokens += max(input_tokens, 0)
    usage.output_tokens += max(output_tokens, 0)
    usage.total_cost_usd = Decimal(usage.total_cost_usd) + cost_usd
