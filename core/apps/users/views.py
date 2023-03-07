from urllib.parse import urljoin

from fastapi import (
    APIRouter,
    Depends,
    Query,
    Request,
    UploadFile,
)
from fastapi.exceptions import HTTPException
from fastapi.responses import (
    JSONResponse,
    RedirectResponse,
)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_jwt_auth import AuthJWT

from dependency_injector.wiring import inject
from starlette import status

from core.apps.users.dependencies import get_current_user
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
from core.common.exceptions import ServiceError
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
    user_service: UserService = Depends(),
    form_data: OAuth2PasswordRequestForm = Depends(),
    Authorize: AuthJWT = Depends(),
):
    user_login_schema = UserLoginSchema(email=form_data.username, password=form_data.password)
    user, error_message = await user_service.authenticate_user(user_login_schema)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_message,
        )

    access_token = Authorize.create_access_token(
        subject=user.id,
        expires_time=config.AUTHORIZATION_TOKEN_EXPIRES_TIMEDELTA,
    )

    return UserLoginSuccessSchema(
        access_token=access_token,
        token_type=config.TOKEN_TYPE,
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
    user_service: UserService = Depends(),
):
    """Initiates the user password reset operation.

    Returns operation result and token cookie. To proceed with password
    reset the request to change password itself should be sent with the
    same token.

    """
    timed_token, error = await user_service.initiate_user_password_reset(
        email=schema.email,
    )

    if error or not timed_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    response_schema = OperationResultSchema(
        status=OperationResultStatusEnum.SUCCESS,
        message='The password resed message has been sent to your email.',
    )
    redirect_url = config.FRONTEND_PASSWORD_RECOVERY_URL.format(token=timed_token)
    await user_service.send_password_reset_email(
        schema.email,
        redirect_url=redirect_url,
    )
    return JSONResponse(content=response_schema.dict())


@router.post(
    '/reset-password/{token}',
    response_model=OperationResultSchema,
    operation_id='resetUserPassword',
)
@inject
async def reset_user_password(
    schema: UserPasswordResetSchema,
    token: str,
    user_service: UserService = Depends(),
):
    """Resets user password."""
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


@router.post(
    '/vk-auth',
    summary='Vk-auth pipeline',
    description='Expects code to be sent from vk-side. Authenticates '
    'user with vk.com. Otherwise, if user is not registered '
    'this handler automaticaly creates new user from vk data.',
    response_model=UserLoginSuccessSchema,
    operation_id='OAuthVK',
)
async def authenticate_via_vk(
    code: str = Query(...),
    user_service: UserService = Depends(),
    Authorize: AuthJWT = Depends(),
):
    try:
        vk_user_data = await user_service.get_vk_user_data_by_code(code=code)
    except ServiceError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error.errors,
        )

    user, _ = await user_service.retrieve(vk_user_id=vk_user_data.user_id)

    if user is None:
        user = await user_service.create_user_via_vk(
            vk_user_id=vk_user_data.user_id,
            first_name=vk_user_data.first_name,
            last_name=vk_user_data.first_name,
            profile_picture_path=vk_user_data.photo_400_orig,
        )

    access_token = Authorize.create_access_token(
        subject=user.id,
        expires_time=config.AUTHORIZATION_TOKEN_EXPIRES_TIMEDELTA,
    )

    return UserLoginSuccessSchema(
        access_token=access_token,
        token_type=config.TOKEN_TYPE,
    )
