from urllib.parse import urljoin

from fastapi import (
    APIRouter,
    Depends,
    Request,
    UploadFile,
)
from fastapi.exceptions import HTTPException
from fastapi.responses import (
    JSONResponse,
    RedirectResponse,
)
from fastapi_jwt_auth import AuthJWT

from dependency_injector.wiring import inject
from starlette import status

from core.apps.users.dependencies import (
    get_current_user,
    get_current_user_optional,
)
from core.apps.users.models import User
from core.apps.users.schemas import (
    ProfilePicturePath,
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
from core.apps.users.services.user_service import UserService
from core.common.config import config
from core.common.enums import OperationResultStatusEnum
from core.common.schemas import OperationResultSchema
from core.scheduler.tasks.user import send_activation_email


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
    schema: UserPasswordResetInitiationSchema,
    request: Request,
    user_service: UserService = Depends(),
):
    """Initiates the user password reset operation.

    Returns operation result and token cookie. To proceed with password
    reset the request to change password itself should be sent with the
    same token.

    """
    token_dto, error = await user_service.initiate_user_password_reset(
        email=schema.email,
    )

    if error or not token_dto:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    response_schema = OperationResultSchema(
        status=OperationResultStatusEnum.SUCCESS,
        message='The password resed message has been sent to your email.',
    )
    redirect_url = urljoin(
        str(request.base_url),
        request.app.url_path_for(
            'confirm_password_reset',
            activation_token=token_dto.activation_token,
        ),
    )
    await user_service.send_password_reset_email(
        token_dto.user_email,
        redirect_url=redirect_url,
    )
    response = JSONResponse(content=response_schema.dict())
    response.set_cookie(key='token', value=token_dto.timed_token)
    return response


@router.get(
    '/confirm-password-reset/{activation_token}',
    operation_id='confirmPasswordReset',
)
async def confirm_password_reset(
    activation_token: str,
    user_service: UserService = Depends(),
):
    """Confirms user password reset."""
    if not await user_service.exists(activation_token=activation_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User not found',
        )

    result, errors = await user_service.confirm_password_reset(
        activation_token=activation_token,
    )

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    if result:
        return RedirectResponse(config.FRONTEND_USER_RESET_PASSWORD_URL)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail='Something went wrong',
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


@router.post(
    '/add-profile-picture',
    status_code=status.HTTP_200_OK,
    response_model=ProfilePicturePath,
    operation_id='addProfilePicture',
)
async def add_profile_picture(
    profile_picture: UploadFile,
    user_services: UserService = Depends(),
    current_user: User = Depends(get_current_user),
):
    """Add Profile Picture."""
    updated_user, errors = await user_services.set_profile_picture(
        profile_picture,
        current_user,
    )

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return updated_user
