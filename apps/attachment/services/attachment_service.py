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


# TODO: здесь всё ужасно, нужен рефакторинг
class AttachmentService(AuthorMixin, CRUDService):
    _repository: AttachmentRepository = AttachmentRepository()
    _assignment_repository: HomeworkAssignmentRepository = HomeworkAssignmentRepository()
    _participation_repository: ParticipationRepository = ParticipationRepository()
    _post_repository: RoomPostRepository = RoomPostRepository()

    async def _can_attach_to_room_post(
        self,
        post_id: int,
    ):
        post = await self._post_repository.retrieve(
            id=post_id,
        )
        participation: Participation = await self._participation_repository.retrieve(
            user_id=self.user.id,
            room_id=post.room_id,
        )
        return participation.can_manage_posts

    async def _can_attach_to_assignment(
        self,
        assignment_id: int,
    ):
        assignment: HomeworkAssignment = await self._post_repository.retrieve(
            id=assignment_id,
        )
        return assignment.author_id == self.user.id

    async def validate_post_id(self, value: int):
        if not await self._can_attach_to_room_post(value):
            return False, 'You can not moderate this room.'
        return True, None

    async def validate_assignment_id(self, value: int):
        if not await self._can_attach_to_assignment(value):
            return False, 'You are not allowed to do that.'
        return True, None
