from typing import (
    Any,
    Tuple,
    Union,
)

from apps.attachment.models import Attachment
from apps.attachment.schemas import AttachmentCreateSchema
from apps.attachment.repositories.attachment_repository import AttachmentRepository
from apps.classroom.models import (
    HomeworkAssignment,
    Participation,
)
from apps.classroom.repositories.assignment import HomeworkAssignmentRepository
from apps.classroom.repositories.participation_repository import ParticipationRepository
from apps.classroom.repositories.post_repository import RoomPostRepository
from apps.common.services.author import AuthorMixin
from apps.common.services.base import CRUDService
from apps.common.config import config


class AttachmentService(AuthorMixin, CRUDService):
    _repository: AttachmentRepository = AttachmentRepository()
    _assignment_repository: HomeworkAssignmentRepository = (
        HomeworkAssignmentRepository()
    )
    _participation_repository: ParticipationRepository = ParticipationRepository()
    _post_repository: RoomPostRepository = RoomPostRepository()
    _post_checked: bool = False
    _assignment_checked: bool = False

    async def _can_attach_to_assignment(
        self,
        assignment_id: int,
    ):
        if self._assignment_checked:
            return True

        assignment: HomeworkAssignment = await self._assignment_repository.retrieve(
            id=assignment_id,
            author_id=self.user.id,
        )
        return bool(assignment)

    async def _can_attach_to_room_post(
        self,
        post_id: int,
    ):
        if self._post_checked:
            return True

        post = await self._post_repository.retrieve(
            id=post_id,
        )
        participation: Participation = await self._participation_repository.retrieve(
            user_id=self.user.id,
            room_id=post.room_id,
        )
        return participation.can_manage_posts

    async def validate_manage_permissions(self, attachment_id: int):
        """ fdbdbfdfbdfbxdfbdb"""
        attachment: Attachment = await self._repository.retrieve(id=attachment_id)

        if attachment.post_id:
            return await self._can_attach_to_room_post(post_id=attachment.post_id)
        if attachment.assignment_id:
            return await self._can_attach_to_assignment(
                assignment_id=attachment.assignment_id
            )
        if attachment.is_profile_picture:
            return self.user.profile_picture_id == attachment_id
        return attachment.author_id == self.user.id

    async def delete_by_id(self, id: int) -> Tuple[bool, Union[dict[str, Any], None]]:
        can_delete_attachment = await self.validate_manage_permissions(attachment_id=id)

        if not can_delete_attachment:
            return False, {'id': 'You are not allowed to do that!'}

        return await self.delete(id=id)

    async def validate_post_id(self, value: int):
        if value is None:
            return True, None

        if not await self._can_attach_to_room_post(value):
            return False, 'You can not moderate this room.'
        self._post_checked = True
        return True, None

    async def validate_assignment_id(self, value: int):
        if value is None:
            return True, None

        if not await self._can_attach_to_assignment(value):
            return False, 'You are not allowed to do that.'
        self._assignment_checked = True
        return True, None

    async def validate_source(
            self,
            file_size: bytes,
    ) -> Tuple[bool, Union[str, None]]:
        if len(file_size) > config.MAX_FILE_SIZE:
            return False, '{filename} size is to large'

        return True, None
