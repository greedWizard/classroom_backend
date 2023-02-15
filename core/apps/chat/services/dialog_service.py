from typing import Optional

from sqlalchemy.exc import IntegrityError

from core.apps.chat.models import Dialog
from core.apps.chat.repositories.dialog_repository import DialogRepository
from core.apps.chat.schemas import DialogCreateSchema
from core.apps.classroom.repositories.participation_repository import ParticipationRepository
from core.apps.users.repositories.user_repository import UserRepository
from core.common.services.base import CRUDService
from core.common.services.decorators import action


class DialogService(CRUDService):
    _repository: DialogRepository = DialogRepository()
    _user_repository: UserRepository = UserRepository()
    _participation_repository: ParticipationRepository = ParticipationRepository()

    async def _add_participants_to_dialog(
        self,
        dialog_id: int,
        participants_ids: list[int],
    ):
        try:
            return await self._repository.add_participants_to_dialog(
                dialog_id=dialog_id,
                participants_ids=participants_ids,
            )
        except IntegrityError:
            return None

    async def _check_manage_dialog_permissions(
        self,
        users_ids: list[str],
    ) -> tuple[bool, Optional[dict[str, str]]]:
        if len(users_ids) < 2:
            return False, {
                'error': 'The number of participants in dialog '
                'should be more than two',
            }
        is_roommates = await self._participation_repository.are_users_rommmates(
            users_ids=users_ids,
        )

        if not is_roommates:
            return False, {'error': 'Users are not rommates.'}
        return True, None

    @action
    async def initialize_dialog(
        self,
        users_ids: list,
        author_id: int,
        join: Optional[list[str]] = None,
    ) -> tuple[Optional[Dialog], Optional[dict[str, str]]]:
        can_initialize_dialog, errors = await self._check_manage_dialog_permissions(
            users_ids=users_ids,
        )

        if not can_initialize_dialog:
            return None, errors

        dialog, errors = await self.create(
            DialogCreateSchema(
                author_id=author_id,
                updated_by_id=author_id,
            ),
        )

        if errors:
            return None, errors

        await self._add_participants_to_dialog(
            dialog_id=dialog.id,
            participants_ids=users_ids,
        )
        return await self._repository.refresh(
            dialog,
            join=join,
        ), errors

    async def start_dialog(
        self,
        participants_ids: list[int],
        author_id: int,
        join: Optional[list[str]] = None,
    ) -> tuple[Optional[Dialog], Optional[dict[str, str]]]:
        """Method gets or creates dialog for student and teacher."""
        users_ids = list(participants_ids)
        users_ids.append(author_id)

        dialog = await self._repository.find_exact_dialog(
            users_ids=users_ids,
            join=join,
        )

        if not dialog:
            return await self.initialize_dialog(
                users_ids=users_ids,
                author_id=author_id,
                join=join,
            )
        return dialog, None

    @action
    async def retrieve_participating_dialog(
        self,
        retriever_id: int,
        dialog_id: int,
        *,
        _join: Optional[list[str]] = None,
        **filters,
    ) -> Dialog:
        if not await self._repository.check_participant_in_dialog(retriever_id, dialog_id):
            return None, {'dialog_id': 'Not found'}
        return await self.retrieve(_join, id=dialog_id, **filters)
