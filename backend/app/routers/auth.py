from datetime import UTC, date, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.database import get_db
from app.core.security import create_access_token, get_current_user, is_admin_email
from app.models.plan import Plan
from app.models.user import User
from app.models.user_usage_monthly import UserUsageMonthly
from app.schemas.auth import CompleteOnboardingRequest, MessageResponse
from app.schemas.common import UserPublic
from app.services.onboarding import activate_pending_user_with_invite
from app.services.oauth import oauth
from app.services.rate_limit import enforce_rate_limit
from app.utils.usage import get_month_period

router = APIRouter(prefix='/auth', tags=['auth'])


def _set_auth_cookie(response: Response, token: str, settings: Settings) -> None:
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=token,
        httponly=True,
        secure=settings.auth_cookie_secure or settings.is_production,
        samesite='lax',
        max_age=settings.jwt_expire_minutes * 60,
        domain=settings.auth_cookie_domain,
        path='/',
    )


@router.get('/google/login')
async def google_login(request: Request, settings: Settings = Depends(get_settings)):
    enforce_rate_limit(key=f'rl:auth:ip:{request.client.host}', limit=settings.auth_rate_limit_per_minute)
    redirect_uri = settings.google_redirect_uri
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get('/google/callback')
async def google_callback(
    request: Request,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    enforce_rate_limit(key=f'rl:auth:ip:{request.client.host}', limit=settings.auth_rate_limit_per_minute)
    token = await oauth.google.authorize_access_token(request)
    userinfo = token.get('userinfo')
    if not userinfo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Google userinfo not available')

    google_sub = userinfo.get('sub')
    email = userinfo.get('email')
    if not google_sub or not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Missing Google identity fields')

    user = db.scalar(select(User).where(User.google_sub == google_sub))
    if user:
        user.name = userinfo.get('name') or user.name
        user.picture_url = userinfo.get('picture') or user.picture_url
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user = User(
            google_sub=google_sub,
            email=email,
            name=userinfo.get('name'),
            picture_url=userinfo.get('picture'),
            is_active=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    plan_code = user.plan.code if user.plan else None
    jwt_token = create_access_token(subject=user.id, email=user.email, plan_code=plan_code, settings=settings)

    redirect_target = f'{settings.frontend_url}/chat' if user.is_active else f'{settings.frontend_url}/onboarding'
    response = RedirectResponse(url=redirect_target, status_code=status.HTTP_302_FOUND)
    _set_auth_cookie(response, jwt_token, settings)
    return response


@router.post('/onboarding/complete', response_model=MessageResponse)
def complete_onboarding(
    payload: CompleteOnboardingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    if current_user.is_active:
        return MessageResponse(message='User already active')

    user, plan = activate_pending_user_with_invite(db, current_user, payload.invite_code)

    period_start, period_end = get_month_period(date.today())
    usage = db.scalar(
        select(UserUsageMonthly).where(
            UserUsageMonthly.user_id == user.id,
            UserUsageMonthly.period_start == period_start,
        )
    )
    if not usage:
        usage = UserUsageMonthly(user_id=user.id, period_start=period_start, period_end=period_end)
        db.add(usage)
        db.commit()

    return MessageResponse(message=f'Onboarding complete. Assigned plan: {plan.code}')


@router.post('/logout', response_model=MessageResponse)
def logout(response: Response, settings: Settings = Depends(get_settings)):
    response.delete_cookie(settings.auth_cookie_name, domain=settings.auth_cookie_domain, path='/')
    return MessageResponse(message='Logged out successfully')


@router.get('/me', response_model=UserPublic)
def me(current_user: User = Depends(get_current_user), settings: Settings = Depends(get_settings)):
    return UserPublic(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        picture_url=current_user.picture_url,
        is_active=current_user.is_active,
        is_admin=is_admin_email(current_user, settings),
    )
