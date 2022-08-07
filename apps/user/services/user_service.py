import re
import string
import uuid
from datetime import (
    datetime,
    timedelta,
)
from hashlib import md5
from typing import (
    Optional,
    Tuple,
    Union,
)

from itsdangerous.exc import BadSignature
from pydantic import BaseModel
from scheduler.tasks.user import send_password_reset_email

from fastapi import UploadFile

from apps.attachment.models import Attachment
from apps.attachment.repositories.attachment_repository import AttachmentRepository
from apps.common.config import config
from apps.common.services.base import (
    CRUDService,
    ResultTuple,
)
from apps.common.services.decorators import action
from apps.common.utils import (
    sign_timed_token,
    unsign_timed_token,
)
from apps.user.constants import (
    EMAIL_REGEX,
    PHONE_REGEX,
)
from apps.user.dto import UserTokenResultDTO
from apps.user.models import User
from apps.user.repositories.user_repository import UserRepository
from apps.user.schemas import (
    UserHyperlinkEmailSchema,
    UserLoginSchema,
    UserPasswordResetSchema,
    UserRegistrationCompleteSchema,
)
from apps.user.utils import resize_image


class UserService(CRUDService):
    _repository: UserRepository = UserRepository()
    _attachment_repository: AttachmentRepository = AttachmentRepository()

    error_messages = {
        'already_exists': 'User with that credits is already registred.',
        'does_not_exist': 'User not found. He is either inactive or not registred yet.',
    }
    schema_map: dict[str, BaseModel] = {
        'create': UserRegistrationCompleteSchema,
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
        password_error = (
            f'Password should be at least {config.MINIMAL_PASSWORD_LENGTH} '
            'characters long and contain at least one digit and upper case letter.'
        )
        repeat_password = self.current_action_attributes.get('repeat_password')

        if not any(upper_char in value for upper_char in string.ascii_uppercase):
            return False, password_error
        if not any(digit in value for digit in string.digits):
            return False, password_error
        if value != repeat_password:
            return False, "Passwords don't match."
        if len(value) < config.MINIMAL_PASSWORD_LENGTH:
            return False, 'Password is too short.'
        return True, {}

    async def validate_first_name(self, value):
        if not value:
            return False, 'The field should not be empty'
        return True, {}

    async def validate_last_name(self, value):
        if not value:
            return False, 'The field should not be empty'
        return True, {}

    async def validate_email(self, value: str) -> ResultTuple:
        if not re.match(EMAIL_REGEX, value):
            return False, 'Invalid email format.'
        if await self._repository.check_email_already_taken(
            email=value,
            user_id=self.current_user_id,
        ):
            return False, 'User with that email is already registred.'
        return True, {}

    async def validate_accept_eula(self, value: bool) -> ResultTuple:
        if not value:
            return False, 'Please accept eula and try again.'
        return True, {}

    async def validate_phone_number(self, value: str) -> ResultTuple:
        if not value:
            return False, 'This field is required'

        if not re.match(PHONE_REGEX, value):
            return False, 'Invalid phone format.'
        if await self._repository.check_phone_number_already_taken(
            user_id=self.current_user_id,
            phone_number=value,
        ):
            return False, 'User with that phone number is already registred.'
        return True, {}

    async def validate_confirm_password(self, value):
        if self._hash_password(value) != self.user.password:
            return False, 'Incorrect password'
        return True, {}

    async def validate_content_type_of_picture(self, content_type: str):
        if not content_type.startswith('image'):
            return False, 'Profile photo must be .png, .jpeg, .jpg'
        return True, {}

    async def validate(self, attrs):
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
        if not any((userLoginSchema.email, userLoginSchema.phone_number)):
            return None, {
                'email': 'this field is required',
                'phone_number': 'this field is required',
            }

        user = await self._repository.get_user_by_auth_credentials(
            password=userLoginSchema.password,
            phone_number=userLoginSchema.phone_number,
            email=userLoginSchema.email,
        )

        if not user:
            return None, 'User not found or inactive'
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
    ) -> Tuple[UserTokenResultDTO, Optional[str]]:
        user = await self._repository.retrieve_active_user(email=email)

        if not user:
            return None, 'User not found'

        user = await self._repository.set_password_reset_deadline(user_id=user.id)
        token = await sign_timed_token(user.id)

        return (
            UserTokenResultDTO(
                timed_token=token,
                activation_token=user.activation_token,
                user_email=user.email,
            ),
            None,
        )

    async def send_password_reset_email(
        self,
        user_email: User,
        redirect_url: str,
    ) -> None:
        send_password_reset_email(
            user=UserHyperlinkEmailSchema(
                email=user_email,
                hyperlink=redirect_url,
            ),
        )

    @action
    async def reset_user_password(
        self,
        password_schema: UserPasswordResetSchema,
        token: str,
    ) -> Tuple[bool, Optional[dict[str, str]]]:
        if not token:
            return None, {'token': 'Token is not provided!'}

        try:
            user_id = await unsign_timed_token(token, salt=config.PASSWORD_RESET_SALT)
        except (TypeError, BadSignature):
            return None, {'token': 'Wrong token format!'}

        user = await self._repository.retrieve_password_reset_needed_user(
            id=user_id,
        )

        if not user:
            return None, {
                'token': 'There is no user with provided token in need of password reset',
            }

        attrs, errors = await self._validate_values(**password_schema.dict())

        if errors:
            return None, errors

        user = await self._repository.close_password_reset(
            user_id,
            new_password=attrs['password'],
        )
        return user, None

    @action
    async def set_profile_picture(
        self,
        profile_photo: UploadFile,
        user: User,
    ) -> Tuple[Union[Attachment, bool], dict[str, str]]:
        _, errors = await self.validate_content_type_of_picture(
            profile_photo.content_type,
        )
        if errors:
            return False, {'content_type_of_profile_photo': errors}

        resized_picture = await resize_image(
            await profile_photo.read(),
            new_size=config.PROFILE_PICTURE_RESOLUTION,
        )

        created_attachment = await self._attachment_repository.create(
            filename=profile_photo.filename,
            source=resized_picture,
        )
        updated_user = await self._repository.update_and_return_single(
            values={
                'profile_picture_id': created_attachment.id,
            },
            id=user.id,
        )

        return updated_user, {}

    @action
    async def confirm_password_reset(
        self,
        password_reset_token: str,
        activation_token: str,
    ) -> Tuple[bool, Optional[dict[str, str]]]:
        if not await self.exists(activation_token=activation_token):
            return None, 'User not found'

        try:
            user_id = await unsign_timed_token(
                password_reset_token,
                salt=config.PASSWORD_RESET_SALT,
            )
        except (TypeError, BadSignature):
            return None, {'token': 'Wrong token format'}

        await self._repository.confirm_password_reset(user_id)
        return True, None
