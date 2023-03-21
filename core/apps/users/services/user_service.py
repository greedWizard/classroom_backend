import re
import string
import uuid
from datetime import (
    datetime,
    timedelta,
)
from hashlib import md5
from typing import (
    Any,
    Optional,
    Tuple,
    Union,
)

from fastapi import UploadFile

from dependency_injector.wiring import (
    inject,
    Provide,
)
from itsdangerous.exc import BadSignature
from starlette import status

from core.apps.attachments.models import Attachment
from core.apps.attachments.repositories.attachment_repository import AttachmentRepository
from core.apps.integrations.authentications.vk.client import VKIntegratioinClient
from core.apps.integrations.authentications.vk.schemas import VKResponseUserInfoSchema
from core.apps.integrations.containers import IntegrationContainer
from core.apps.integrations.exceptions import IntegrationException
from core.apps.localization.utils import translate as _
from core.apps.users.constants import EMAIL_REGEX
from core.apps.users.models import User
from core.apps.users.repositories.user_repository import UserRepository
from core.apps.users.schemas import (
    UserLoginSchema,
    UserPasswordResetSchema,
)
from core.apps.users.utils import resize_image
from core.common.config import config
from core.common.exceptions import ServiceError
from core.common.services.base import (
    CRUDService,
    ResultTuple,
)
from core.common.services.decorators import action
from core.common.utils import (
    get_attachment_path,
    sign_timed_token,
    unsign_timed_token,
)
from core.scheduler.tasks.user import send_password_reset_email


class UserService(CRUDService):
    _repository: UserRepository = UserRepository()
    _attachment_repository: AttachmentRepository = AttachmentRepository()

    error_messages = {
        'create': _('User with that credits is already registred.'),
        'does_not_exist': _('User not found. He is either inactive or not registred yet.'),
    }

    def set_user(self, user: User):
        self.user = user

    @property
    def current_user_id(self):
        user_id = None

        if self.user:
            user_id = self.user.id
        return user_id

    def _hash_password(self, password: str) -> str:
        return md5(password.encode()).hexdigest()  # no qa

    async def validate_password(self, value: str) -> ResultTuple:
        if self.user is not None and self.user.is_external and not value:
            return True, None

        password_error_text = _(
            'Password should be at least {LENGTH} '
            'characters long and contain at least one digit and upper case letter.',
        )
        password_error = password_error_text.format(LENGTH=config.MINIMAL_PASSWORD_LENGTH)
        repeat_password = self.current_action_attributes.get('repeat_password')

        if not any(upper_char in value for upper_char in string.ascii_uppercase):
            return False, password_error
        if not any(digit in value for digit in string.digits):
            return False, password_error
        if value != repeat_password:
            return False, _("Passwords don't match.")
        if len(value) < config.MINIMAL_PASSWORD_LENGTH:
            return False, _('Password is too short.')
        return True, None

    async def validate_first_name(self, value) -> ResultTuple:
        if not value:
            return False, _('The field should not be empty')
        return True, None

    async def validate_last_name(self, value) -> ResultTuple:
        if not value:
            return False, _('The field should not be empty')
        return True, None

    async def validate_email(self, value: str) -> ResultTuple:
        if self.user is not None and self.user.is_external and not value:
            return True, None
        if not re.match(EMAIL_REGEX, value):
            return False, _('Invalid email format.')
        if await self._repository.check_email_already_taken(
            email=value,
            user_id=self.current_user_id,
        ):
            return False, _('User with that email is already registred.')
        return True, None

    async def validate_accept_eula(self, value: bool) -> ResultTuple:
        if not value:
            return False, _('Please accept eula and try again.')
        return True, None

    async def validate_confirm_password(self, value: str) -> ResultTuple:
        if not self.user.password and self.user.is_external:
            return True, None
        if self._hash_password(value) != self.user.password:
            return False, _('Incorrect password')
        return True, None

    async def validate_content_type_of_picture(self, content_type: str) -> ResultTuple:
        if not content_type.startswith('image'):
            return _('Profile photo must be .png, .jpeg, .jpg')
        return None

    async def validate(self, attrs: dict[str, Any]):
        password = attrs.get('password')

        if password:
            attrs['password'] = self._hash_password(password)
            attrs.pop('repeat_password', None)

        if self.action == 'create':
            attrs['activation_token'] = uuid.uuid4().hex
            attrs['activation_deadline_dt'] = datetime.utcnow() + timedelta(
                hours=config.ACTIVATION_DEADLINE_HOURS,
            )
            attrs['is_active'] = False
            attrs.pop('accept_eula')
        return await super().validate(attrs)

    @action
    async def authenticate_user(
        self,
        userLoginSchema: UserLoginSchema,
    ) -> Tuple[User, str]:
        if not userLoginSchema.email:
            return None, {
                'email': _('this field is required'),
            }

        user = await self._repository.get_user_by_auth_credentials(
            password=userLoginSchema.password,
            email=userLoginSchema.email,
        )

        if not user:
            return None, _('User not found or inactive')
        await self._repository.update_last_login(user)
        return user, None

    @action
    async def activate_user(self, activation_token: str) -> Tuple[User, dict]:
        activated_user = await self._repository.activate_user(activation_token)

        if not activated_user:
            return False
        return True

    @action
    async def initiate_user_password_reset(
        self,
        email: str,
    ) -> Tuple[str, Optional[str], Optional[User]]:
        user = await self._repository.retrieve_active_user(email=email)

        if not user:
            return None, _('User not found')

        user = await self._repository.set_password_reset_deadline(user_id=user.id)
        token = await sign_timed_token(user.id)

        return token, None, user

    async def send_password_reset_email(
        self,
        schema: User,
        localization: str,
    ) -> None:
        send_password_reset_email(
            user=schema,
            localization=localization,
        )

    @action
    async def reset_user_password(
        self,
        password_schema: UserPasswordResetSchema,
        token: str,
    ) -> Tuple[bool, Optional[dict[str, str]]]:
        if not token:
            return None, {'token': _('Token is not provided!')}

        try:
            user_id = await unsign_timed_token(token, salt=config.PASSWORD_RESET_SALT)
        except (TypeError, BadSignature):
            return None, {'token': _('Wrong token format!')}

        user = await self._repository.retrieve_password_reset_needed_user(
            id=user_id,
        )

        if not user:
            return None, {
                'token': _('There is no user with provided token in need of password reset'),
            }

        attrs, errors = await self._validate_values(**password_schema.dict())

        if errors:
            return None, errors

        user = await self._repository.close_password_reset(
            user_id,
            new_password=attrs['password'],
        )
        return user, None

    async def _upload_profile_picture(
        self,
        profile_photo: UploadFile,
    ) -> tuple[Optional[str], Optional[dict]]:
        errors = await self.validate_content_type_of_picture(
            profile_photo.content_type,
        )

        if errors:
            return None, {'content_type_of_profile_photo': errors}

        resized_picture = await resize_image(
            await profile_photo.read(),
            new_size=config.PROFILE_PICTURE_RESOLUTION,
        )

        created_attachment = await self._attachment_repository.create(
            filename=profile_photo.filename,
            source=resized_picture,
        )
        return get_attachment_path(created_attachment.id), None

    @action
    async def set_profile_picture(
        self,
        profile_photo: UploadFile,
        user: User,
    ) -> Tuple[Union[Attachment, bool], dict[str, str]]:
        profile_picture_path, errors = await self._upload_profile_picture(
            profile_photo=profile_photo,
        )

        if errors is not None:
            return None, errors

        updated_user = await self._repository.update_and_return_single(
            values={
                'profile_picture_path': profile_picture_path,
            },
            id=user.id,
        )

        return updated_user, None

    @action
    async def confirm_password_reset(
        self,
        activation_token: str,
    ) -> Tuple[bool, Optional[dict[str, str]]]:
        if not await self.exists(activation_token=activation_token):
            return None, _('User not found')
        await self._repository.confirm_password_reset(activation_token=activation_token)
        return True, None

    @action
    @inject
    async def get_vk_user_data_by_code(
        self,
        code: str,
        vk_integration_client: VKIntegratioinClient = Provide[IntegrationContainer.vk_integration_client],
    ) -> Optional[VKResponseUserInfoSchema]:
        try:
            access_data = await vk_integration_client.get_user_access_data(code=code)
        except IntegrationException as error:
            raise ServiceError(
                status_code=status.HTTP_403_FORBIDDEN,
                errors={'vk': str(error)},
            )

        return await vk_integration_client.get_user_data(
            access_token=access_data.access_token,
            user_id=access_data.user_id,
        )

    @action
    async def create_user_via_vk(
        self,
        vk_user_id: int,
        first_name: str,
        last_name: str,
        profile_picture_path: Optional[str] = None,
    ):
        if await self._repository.exists(vk_user_id=vk_user_id):
            raise ServiceError(
                status_code=status.HTTP_400_BAD_REQUEST, errors={
                    'vk_user_id': _('User with that vk id already exists!'),
                },
            )
        return await self._repository.create(
            first_name=first_name,
            last_name=last_name,
            vk_user_id=vk_user_id,
            profile_picture_path=profile_picture_path,
            is_active=True,
        )
