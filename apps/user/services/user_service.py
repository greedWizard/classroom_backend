import re
import string
import uuid
from datetime import (
    datetime,
    timedelta,
)
from hashlib import md5
from typing import Tuple

from pydantic import BaseModel

from apps.common.config import config
from apps.common.services.base import (
    CRUDService,
    ResultTuple,
)
from apps.common.services.decorators import action
from apps.user.constants import (
    EMAIL_REGEX,
    PHONE_REGEX,
)
from apps.user.models import User
from apps.user.repositories.user_repository import UserRepository
from apps.user.schemas import (
    UserLoginSchema,
    UserRegistrationCompleteSchema,
)
from apps.user.utils import hash_string


class UserService(CRUDService):
    _repository: UserRepository = UserRepository()
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

        if not any(upper_char in value for upper_char in string.ascii_uppercase):
            return False, password_error
        if not any(digit in value for digit in string.digits):
            return False, password_error
        if value != self.current_action_attributes.get('repeat_password'):
            return False, "Passwords don't match."
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
        if self.action == 'update':
            attrs.pop('confirm_password')
        return await super().validate(attrs)

    async def has_update_permission(
        self,
        user: User,
        confirm_password: str,
    ):
        if user.password != self._hash_password(confirm_password):
            return False, 'Incorrect password.'
        return True, None

    @action
    async def authenticate_user(
        self,
        userLoginSchema: UserLoginSchema,
    ) -> Tuple[User, str]:
        user = await self._repository.filter(
            Q(email=userLoginSchema.email)
            | Q(phone_number=userLoginSchema.phone_number),
            password=hash_string(userLoginSchema.password),
        ).first()

        if not user:
            return None, 'Bad credentials'
        if not user.is_active:
            return None, 'User is not active. Please activate your profile.'

        user.last_login = datetime.utcnow()
        await user.save()

        return user, None

    @action
    async def activate_user(self, activation_token: str) -> Tuple[User, dict]:
        user = await self._repository.filter(
            is_active=False,
            activation_token=activation_token,
        ).first()

        if not user:
            return None, {'activation_token': 'User not found'}
        user.is_active = True
        await user.save()

        return user, None
