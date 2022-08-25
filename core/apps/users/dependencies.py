from fastapi import Depends
from fastapi_jwt_auth import AuthJWT

from core.apps.users.exceptions import NotAuthenticatedException
from core.apps.users.models import User
from core.apps.users.services.user_service import UserService


async def _get_current_user(
    Authorize: AuthJWT = Depends(),
    user_service: UserService = Depends(),
):
    user_id = Authorize.get_jwt_subject()
    current_user, _ = await user_service.retrieve(id=user_id)
    return current_user


async def get_current_user(
    current_user: User = Depends(_get_current_user),
):
    if not current_user:
        raise NotAuthenticatedException()
    return current_user


async def websocket_user(
    token: str,
):
    Authorize = AuthJWT()
    user_service = UserService()

    Authorize.jwt_required('websocket', token=token)
    user_id = Authorize.get_raw_jwt(token)['sub']

    current_user, _ = await user_service.retrieve(id=user_id)

    return current_user


async def get_current_user_optional(
    current_user: User = Depends(_get_current_user),
):
    return current_user
