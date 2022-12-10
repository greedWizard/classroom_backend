from typing import Optional

from core.apps.chat.models import Message
from core.apps.chat.repositories.dialog_repository import DialogRepository
from core.apps.chat.repositories.message_repository import MessageRepository
from core.apps.localization.utils import translate as _
from core.common.services.base import CRUDService
from core.common.services.decorators import action


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
            return False, _('You are not participating in this dialog!')
        return True, None

    @action
    async def fetch_by_dialog_id(
        self,
        user_id: int,
        dialog_id: int,
        _ordering: list[str] = None,
        join: list[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
        **filters,
    ):
        if not await self._dialog_repository.check_participant_in_dialog(
            participant_id=user_id,
            dialog_id=dialog_id,
        ):
            return None, {'detail': _('You are not participating in this dialog!')}
        return await super().fetch(
            _ordering,
            join,
            dialog_id=dialog_id,
            limit=limit,
            offset=offset,
            **filters,
        )

    @action
    async def get_unique_last_messages(
        self,
        user_id: int,
        ordering: Optional[list[str]] = None,
        join: Optional[list[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **filters,
    ):
        if not ordering:
            ordering = []

        ordering.insert(0, '-created_at')

        return await self._repository.get_unique_last_messages(
            ordering=ordering,
            join=join,
            limit=limit,
            offset=offset,
            user_id=user_id,
            **filters,
        )
