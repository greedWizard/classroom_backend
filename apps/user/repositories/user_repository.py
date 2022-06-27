from typing import Union

from apps.common.repositories.base import CRUDRepository
from apps.user.models import User


class UserRepository(CRUDRepository):
    _model: User = User

    async def check_email_already_taken(
        self,
        email: str,
        user_id: Union[int, None],
    ) -> bool:
        return await self.exists(email=email, id=user_id)

    async def check_phone_number_already_taken(
        self,
        phone_number: str,
        user_id: Union[int, None],
    ) -> bool:
        return await self.exists(phone_number=phone_number, id=user_id)
