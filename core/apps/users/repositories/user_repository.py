import uuid
from typing import Union

from core.apps.users.models import User
from core.apps.users.utils import hash_string
from core.common.config import config
from core.common.repositories.base import CRUDRepository
from core.common.utils import get_current_datetime

from sqlalchemy import (
    func,
    select,
)


class UserRepository(CRUDRepository):
    _model: User = User

    async def check_email_already_taken(
        self,
        email: str,
        user_id: Union[int, None],
    ) -> bool:
        statement = select(func.count(self._model.id)).filter(
            self._model.id != user_id,
            self._model.email == email,
        )

        return await self.get_scalar(statement)

    async def check_phone_number_already_taken(
        self,
        phone_number: str,
        user_id: Union[int, None],
    ) -> bool:
        statement = select(func.count(self._model.id)).filter(
            self._model.id != user_id,
            self._model.phone_number == phone_number,
        )

        return await self.get_scalar(statement)

    async def update_last_login(self, user: User) -> User:
        await self.update({'last_login': get_current_datetime()}, id=user.id)

    async def get_user_by_auth_credentials(
        self,
        password: str,
        phone_number: str = None,
        email: str = None,
    ):
        async with self.get_session() as session:
            statement = select(self._model).filter(
                self._model.password == hash_string(password),
                self._model.is_active == True,
                (self._model.email == email)
                | (self._model.phone_number == phone_number),
            )
            return (await session.execute(statement)).scalars().first()

    async def activate_user(
        self,
        activation_token: str,
    ) -> Union[User, None]:
        """Activates inactive user with provided activation token.

        If user wasn't found returns None.

        """
        user = await self.retrieve(
            activation_token=activation_token,
            is_active=False,
        )
        if user:
            user = await self.update_object(user, is_active=True)
        return user

    async def retrieve_active_user(
        self,
        **filters,
    ):
        filters['is_active'] = True
        return await self.retrieve(**filters)

    async def set_password_reset_deadline(self, user_id: int) -> _model:
        return await self.update_and_return_single(
            values={
                'is_reset_needed': False,
                'password_reset_deadline': get_current_datetime()
                + config.RESET_PASSWORD_TIMEDELTA,
                'activation_token': uuid.uuid4().hex,
            },
            id=user_id,
        )

    async def confirm_password_reset(self, activation_token: str) -> _model:
        # TODO: filters gt(e)
        confirmed_user: User = await self.retrieve(activation_token=activation_token)

        if not confirmed_user:
            return None

        if get_current_datetime() >= confirmed_user.password_reset_deadline:
            return None

        async with self.get_session() as session:
            confirmed_user.is_reset_needed = True
            session.add(confirmed_user)
            await session.commit()
            return confirmed_user

    async def close_password_reset(self, user_id: int, new_password: str) -> _model:
        return await self.update(
            values={
                'is_reset_needed': False,
                'password_reset_deadline': None,
                'password': new_password,
            },
            id=user_id,
        )

    async def retrieve_password_reset_needed_user(self, id: int) -> _model:
        async with self.get_session() as session:
            statement = select(self._model).filter(
                self._model.id == id,
                self._model.is_reset_needed == True,
                self._model.password_reset_deadline >= get_current_datetime(),
            )
            user = (await session.execute(statement)).scalars().first()
        return user
