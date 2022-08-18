from core.apps.chat.models import (
    Dialog,
    Message,
)
from core.apps.chat.services.mixins import ChatPermissionsMixin
from core.common.services.base import CRUDService
from core.common.services.decorators import action
from tortoise.expressions import Q


class MessageService(ChatPermissionsMixin, CRUDService):
    model: type[Message] = Message

    async def get_queryset(self, management: bool = False):
        qs = await super().get_queryset(management)
        return qs.filter(Q(sender_id=self.sender.id) | Q(reciever_id=self.sender.id))

    @action
    async def fetch_last(self):
        # TODO: Рефакторить
        queryset = await self.get_queryset()

        messages = await queryset.prefetch_related(
            'sender',
            'reciever',
            'dialog__reciever',
            'dialog__sender',
            'dialog',
        ).order_by('-created_at')
        # TODO: черепаха серьёзно не умеет юзать distinct + order_by
        distinct_messages = []
        dialog_ids = []

        for message in messages:
            if message.dialog_id not in dialog_ids:
                distinct_messages.append(message)
                dialog_ids.append(message.dialog_id)

        return distinct_messages

    async def fetch_for_dialog(self, dialog: Dialog):
        qs = await self.get_queryset()
        return await qs.filter(dialog=dialog).prefetch_related('sender', 'reciever')
