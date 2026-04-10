from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.core.security import get_current_user, is_admin_email
from app.models.user import User
from app.schemas.common import UserPublic

router = APIRouter(tags=['me'])


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
