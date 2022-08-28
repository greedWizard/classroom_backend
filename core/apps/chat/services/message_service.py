from typing import Optional

from core.apps.chat.models import Message
from core.apps.chat.repositories.dialog_repository import DialogRepository
from core.apps.chat.repositories.message_repository import MessageRepository
from core.common.services.base import CRUDService


class MessageService(CRUDService):
    _repository: MessageRepository = MessageRepository()
    _dialog_repository: DialogRepository = DialogRepository()

    async def validate_dialog_id(
        self,
        value: int,
    ) -> tuple[Optional[Message], Optional[dict[str, str]]]:
        sender_id = self.current_action_attributes['sender_id']

        if not await self._dialog_repository.check_participant_in_dialog(
            participant_id=sender_id,
            dialog_id=value,
        ):
            return False, 'You are not participating in this dialog!'
        return True, None
