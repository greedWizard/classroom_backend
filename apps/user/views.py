from urllib.parse import urljoin

from fastapi_jwt_auth import AuthJWT
from scheduler.tasks.user import send_activation_email
from starlette import status

from fastapi import (
    APIRouter,
    Depends,
    Request,
)
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse

from apps.common.config import config
from apps.user.dependencies import (
    get_current_user,
    get_current_user_optional,
)
from apps.user.models import User
from apps.user.schemas import (
    UserActivationEmailSchema,
    UserLoginSchema,
    UserLoginSuccessSchema,
    UserProfileSchema,
    UserProfileUpdateSchema,
    UserRegisterSchema,
    UserRegistrationCompleteSchema,
)
from apps.user.services.user_service import UserService


router = APIRouter(
    tags=['user'],
)


@router.get(
    '/activate/{activation_token}',
    operation_id='activateUser',
)
async def activate_user(
    activation_token: str,
    user_service: UserService = Depends(),
):
    await user_service.activate_user(activation_token)
    return RedirectResponse(config.FRONTEND_LOGIN_URL)


@router.post(
    '/register',
    response_model=UserRegistrationCompleteSchema,
    status_code=status.HTTP_201_CREATED,
    operation_id='registerUser',
)
async def register_user(
    request: Request,
    userRegisterSchema: UserRegisterSchema,
    user_service: UserService = Depends(),
):
    user, errors = await user_service.create(userRegisterSchema)

    if not errors:
        activation_link = urljoin(
            str(request.base_url),
            request.app.url_path_for(
                'activate_user',
                activation_token=user.activation_token,
            ),
        )
        send_activation_email(
            user=UserActivationEmailSchema(
                email=user.email,
                activation_link=activation_link,
            ),
        )
        return user
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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You are already logged in!',
        )

    user, error_message = await user_service.authenticate_user(userLoginSchema)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_message,
        )

    # TODO: отдельно создавать access_token и refresh_token
    access_token = Authorize.create_access_token(
        subject=user.id,
        expires_time=config.AUTHORIZATION_TOKEN_EXPIRES_TIMEDELTA,
    )
    refresh_token = Authorize.create_refresh_token(
        subject=user.id,
        expires_time=config.AUTHORIZATION_TOKEN_EXPIRES_TIMEDELTA,
    )

    return UserLoginSuccessSchema(
        access_token=access_token,
        refresh_token=refresh_token,
    )


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
    user, errors = await user_service.update(
        id=current_user.id,
        updateSchema=userUpdateSchema,
    )

    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=errors,
        )
    return user
