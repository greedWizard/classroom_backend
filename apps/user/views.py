from urllib.parse import urljoin

from dependency_injector.wiring import inject
from fastapi_jwt_auth import AuthJWT
from scheduler.tasks.user import send_activation_email
from starlette import status

from fastapi import (
    APIRouter,
    Depends,
    Request,
)
from fastapi.exceptions import HTTPException
from fastapi.responses import (
    JSONResponse,
    RedirectResponse,
)

from apps.common.config import config
from apps.common.enums import OperationResultStatusEnum
from apps.common.schemas import OperationResultSchema
from apps.user.dependencies import (
    get_current_user,
    get_current_user_optional,
)
from apps.user.models import User
from apps.user.schemas import (
    UserHyperlinkEmailSchema,
    UserLoginSchema,
    UserLoginSuccessSchema,
    UserPasswordResetInitiationSchema,
    UserPasswordResetSchema,
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
            user=UserHyperlinkEmailSchema(
                email=user.email,
                hyperlink=activation_link,
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


@router.post(
    '/request-reset-password',
    response_model=OperationResultSchema,
    operation_id='initiateUserPasswordReset',
)
async def initiate_user_password_reset(
    request: Request,
    schema: UserPasswordResetInitiationSchema,
    user_service: UserService = Depends(),
):
    """Initiates the user password reset operation.

    Returns operation result and token cookie. To proceed with password
    reset the request to change password itself should be sent with the
    same token.

    """
    token, error = await user_service.initiate_user_password_reset(
        email=schema.email,
        redirect_url=config.FRONTEND_USER_RESET_PASSWORD_URL,
    )

    if token:
        response_schema = OperationResultSchema(
            status=OperationResultStatusEnum.SUCCESS,
            message='The password resed message has been sent to your email.',
        )
        response = JSONResponse(content=response_schema.dict())
        response.set_cookie(key='token', value=token)
        return response
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=error,
    )


@router.post(
    '/reset-password',
    response_model=OperationResultSchema,
    operation_id='resetUserPassword',
)
@inject
async def reset_user_password(
    request: Request,
    schema: UserPasswordResetSchema,
    user_service: UserService = Depends(),
):
    """Resets user password."""
    token = request.cookies.get('token')
    _, errors = await user_service.reset_user_password(
        password_schema=schema,
        token=token,
    )

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return OperationResultSchema(
        status=OperationResultStatusEnum.SUCCESS,
        message='Password has been reset! Please relogin to start a new session!',
    )
