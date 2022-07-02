from typing import Any

from tortoise.models import Model

from apps.user.models import User


class ChatPermissionsMixin:
    sender_field: str = 'recipient'
    reciever_field: str = 'sender'
    model: type[Model] = NotImplemented

    def __init__(self, sender: User) -> None:
        self.sender = sender

    async def validate(self, attrs: list[dict[str, Any]]) -> list[dict[str, Any]]:
        attrs = await super().validate(attrs)
        attrs['sender_id'] = self.sender.id

        return attrs
