from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.invite_code import InviteCode
from app.models.plan import Plan
from app.models.user import User


def validate_invite_code(db: Session, code: str) -> InviteCode:
    invite = db.scalar(select(InviteCode).where(InviteCode.code == code))
    now = datetime.now(UTC)
    if not invite or not invite.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid invite code')
    if invite.expires_at and invite.expires_at < now:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invite code expired')
    if invite.used_count >= invite.max_uses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invite code usage limit reached')
    return invite


def activate_pending_user_with_invite(db: Session, user: User, invite_code: str) -> tuple[User, Plan]:
    invite = validate_invite_code(db, invite_code)
    plan = db.scalar(select(Plan).where(Plan.id == invite.assigned_plan_id))
    if not plan:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Assigned plan does not exist')

    user.plan_id = plan.id
    user.is_active = True
    invite.used_count += 1
    if invite.used_count >= invite.max_uses:
        invite.is_active = False

    db.add_all([user, invite])
    db.commit()
    db.refresh(user)
    return user, plan
