from tortoise.expressions import Q

from apps.chat.models import Dialog
from apps.user.models import User
from common.services.base import CRUDService


class DialogService(CRUDService):
    model: type[Dialog] = Dialog

    @classmethod
    async def check_dialog_exists(
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
            .prefetch_related(
                'messages',
                'sender',
                'reciever',
                'messages__sender',
                'messages__reciever',
            )
            .first()
        )
        return (True, dialog) if dialog else (False, None)

    # TODO: валидация, что начинать диалог могут только ученики с преподавателем
