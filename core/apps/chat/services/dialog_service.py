from typing import Union

from core.apps.chat.models import Dialog
from core.apps.chat.services.mixins import ChatPermissionsMixin
from core.apps.users.models import User
from core.common.services.base import CRUDService
from core.common.services.decorators import action
from tortoise.expressions import Q


class DialogService(ChatPermissionsMixin, CRUDService):
    model: type[Dialog] = Dialog
    fields_for_chat = [
        'messages',
        'sender',
        'reciever',
        'messages__sender',
        'messages__reciever',
    ]

    async def get_queryset(self, management: bool = False):
        qs = await super().get_queryset(management)
        return qs.filter(Q(sender_id=self.sender.id) | Q(reciever_id=self.sender.id))

    @classmethod
    async def get_dialog(
        cls,
        sender_id: User,
        reciever_id: User,
    ) -> tuple[bool, Dialog]:
        dialog = (
            await cls.model.filter(
                Q(
                    sender_id=sender_id,
                    reciever_id=reciever_id,
                )
                | Q(
                    reciever_id=sender_id,
                    sender_id=reciever_id,
                ),
            )
            .prefetch_related(*cls.fields_for_chat)
            .first()
        )
        return (True, dialog) if dialog else (False, None)

    # TODO: валидация, что начинать диалог могут только ученики с преподавателем

    @action
    async def fetch_for_user(
        self,
        user: User,
    ) -> tuple[list[Dialog], Union[dict[str, str], None]]:
        pass
