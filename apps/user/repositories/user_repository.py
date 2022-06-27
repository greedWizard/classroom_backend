from typing import Union

from sqlalchemy import (
    func,
    select,
)

from apps.common.repositories.base import CRUDRepository
from apps.user.models import User


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
