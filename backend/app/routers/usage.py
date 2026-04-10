from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_active_user
from app.models.user import User
from app.models.user_usage_monthly import UserUsageMonthly
from app.schemas.usage import UsageMonthlyPublic
from app.services.quota import get_or_create_current_usage

router = APIRouter(prefix='/usage', tags=['usage'])


@router.get('', response_model=UsageMonthlyPublic)
def get_current_usage(current_user: User = Depends(require_active_user), db: Session = Depends(get_db)):
    return get_or_create_current_usage(db, current_user)


@router.get('/history', response_model=list[UsageMonthlyPublic])
def get_usage_history(current_user: User = Depends(require_active_user), db: Session = Depends(get_db)):
    return list(
        db.scalars(
            select(UserUsageMonthly)
            .where(UserUsageMonthly.user_id == current_user.id)
            .order_by(UserUsageMonthly.period_start.desc())
            .limit(12)
        )
    )
