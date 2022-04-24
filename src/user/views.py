from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT

from starlette import status

from core.config import config
from user.models import User
from user.schemas import (
    UserLoginSchema,
    UserLoginSuccessSchema,
    UserProfileSchema,
    UserProfileUpdateSchema,
    UserRegisterSchema,
    UserRegistrationCompleteSchema,
)
from user.services.user_service import UserService
from user.utils import get_current_user, get_current_user_optional


router = APIRouter(
    tags=['authentication'],
)


@router.post(
    '/register',
    response_model=UserRegistrationCompleteSchema,
    status_code=status.HTTP_201_CREATED,
    operation_id='registerUser',
)
async def register_user(
    userRegisterSchema: UserRegisterSchema,
    user_service: UserService = Depends(),
):
    _, errors = await user_service.create(userRegisterSchema)

    if not errors:
        return UserRegistrationCompleteSchema(status=config.USER_SUCCESS_STATUS)
    raise HTTPException(detail=errors, status_code=status.HTTP_400_BAD_REQUEST)


@router.post(
    '/authenticate',
    response_model=UserLoginSuccessSchema,
    operation_id='authenticateUser',
)
async def authenticate_user(
    userLoginSchema: UserLoginSchema,
    current_user: User = Depends(get_current_user_optional),
    user_service: UserService = Depends(),
    Authorize: AuthJWT = Depends(),
):
    if current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are already logged in!')
    print(current_user)

    user, error_message = await user_service.authenticate_user(userLoginSchema)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=error_message)

    access_token = Authorize.create_access_token(
        subject=user.id,
        expires_time=config.AUTHORIZATION_TOKEN_EXPIRES_TIMEDELTA,
    )
    refresh_token = Authorize.create_refresh_token(
        subject=user.id,
        expires_time=config.AUTHORIZATION_TOKEN_EXPIRES_TIMEDELTA,
    )

    return UserLoginSuccessSchema(access_token=access_token, refresh_token=refresh_token)


@router.get(
    '/profile/current',
    response_model=UserProfileSchema,
    operation_id='currentUserInfo',
)
async def current_user_info(
    user: User = Depends(get_current_user),
):
    return UserProfileSchema.from_orm(user)


@router.get(
    '/profile/{user_id}',
    response_model=UserProfileSchema,
    operation_id='userInfo',
)
async def user_info(
    user_id: int,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(),
):
    user, error_message = await user_service.retrieve(id=user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)
    return UserProfileSchema.from_orm(user)


@router.put(
    '/profile/current',
    response_model=UserProfileSchema,
    operation_id='updateCurrentUser',
)
async def update_current_user(
    userUpdateSchema: UserProfileUpdateSchema,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(),
):
    user_service.set_user(current_user)
    user, errors = await user_service.update(current_user.id, userUpdateSchema)

    if errors.get('confirm_password'):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=errors)

    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=errors,
        )
    return UserProfileSchema.from_orm(user)
