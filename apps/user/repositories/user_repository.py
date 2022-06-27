from typing import Union

from sqlalchemy import (
    func,
    select,
)

from apps.common.repositories.base import CRUDRepository
from apps.common.repositories.exceptions import RepositoryException
from apps.user.models import User
from apps.user.utils import hash_string


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

    async def get_user_by_auth_credentials(
        self,
        password: str,
        phone_number: str = None,
        email: str = None
    ):
        async with self.get_session() as session:
            statement = select(self._model).filter(
                self._model.password == hash_string(password),
                (self._model.email == email) | (self._model.phone_number == phone_number)
            )
            return (await session.execute(statement)).scalars().first()

    async def activate_user(
        self,
        activation_token: str,
    ) -> Union[User, None]:
        '''
        Activates inactive user with provided activation token.
        If user wasn't found returns None.
        '''
        user = await self.retrieve(
            activation_token=activation_token,
            is_active=False,
        )
        user = await self.update_object(user, is_active=True)
        return user