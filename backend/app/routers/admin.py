import secrets
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_admin
from app.models.invite_code import InviteCode
from app.models.plan import Plan
from app.models.user import User
from app.schemas.admin import (
    AdminInviteCodePublic,
    AdminPlanPublic,
    AdminUserPublic,
    AssignPlanRequest,
    InviteCodeCreateRequest,
)
from app.schemas.auth import MessageResponse

router = APIRouter(prefix='/admin', tags=['admin'])


@router.get('/users', response_model=list[AdminUserPublic])
def list_users(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return list(db.scalars(select(User).order_by(User.created_at.desc()).limit(500)))


@router.post('/users/{user_id}/plan', response_model=MessageResponse)
def assign_plan(
    user_id: UUID,
    payload: AssignPlanRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    plan = db.scalar(select(Plan).where(Plan.code == payload.plan_code))
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Plan not found')
    user.plan_id = plan.id
    db.add(user)
    db.commit()
    return MessageResponse(message=f'User plan updated to {plan.code}')


@router.post('/users/{user_id}/disable', response_model=MessageResponse)
def disable_user(user_id: UUID, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    user.is_active = False
    db.add(user)
    db.commit()
    return MessageResponse(message='User disabled')


@router.post('/users/{user_id}/enable', response_model=MessageResponse)
def enable_user(user_id: UUID, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    user.is_active = True
    db.add(user)
    db.commit()
    return MessageResponse(message='User enabled')


@router.get('/plans', response_model=list[AdminPlanPublic])
def list_plans(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return list(db.scalars(select(Plan).order_by(Plan.code.asc())))


@router.post('/invite-codes', response_model=AdminInviteCodePublic)
def create_invite_code(
    payload: InviteCodeCreateRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    plan = db.scalar(select(Plan).where(Plan.code == payload.assigned_plan_code))
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Plan not found')

    code = payload.code.strip() if payload.code else secrets.token_urlsafe(12)
    existing = db.scalar(select(InviteCode).where(InviteCode.code == code))
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invite code already exists')

    if payload.expires_at and payload.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='expires_at cannot be in the past')

    invite = InviteCode(
        code=code,
        created_by=admin.id,
        assigned_plan_id=plan.id,
        max_uses=payload.max_uses,
        used_count=0,
        expires_at=payload.expires_at,
        is_active=True,
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite


@router.get('/invite-codes', response_model=list[AdminInviteCodePublic])
def list_invite_codes(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    return list(db.scalars(select(InviteCode).order_by(InviteCode.created_at.desc()).limit(500)))


@router.post('/invite-codes/{invite_id}/revoke', response_model=MessageResponse)
def revoke_invite_code(invite_id: UUID, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    invite = db.scalar(select(InviteCode).where(InviteCode.id == invite_id))
    if not invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invite code not found')
    invite.is_active = False
    db.add(invite)
    db.commit()
    return MessageResponse(message='Invite code revoked')
