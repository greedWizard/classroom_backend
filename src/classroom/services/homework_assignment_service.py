
from functools import partialmethod
from typing import Union

from tortoise.expressions import Q

from classroom.constants import HomeWorkAssignmentStatus, ParticipationRoleEnum, RoomPostType
from classroom.models import HomeworkAssignment, Participation, Room
from classroom.schemas import HomeworkAssignmentRequestChangesSchema
from classroom.services.room_post_service import RoomPostService

from core.services.author import AuthorMixin
from core.services.base import CRUDService
from core.services.decorators import action


class HomeworkAssignmentService(AuthorMixin, CRUDService):
    model = HomeworkAssignment

    @property
    def room_post_service(self):
        return RoomPostService(self.user)

    def _check_is_status_restricted(self, assignment: HomeworkAssignment):
        return assignment.status == HomeWorkAssignmentStatus.done

    async def get_queryset(self, management: bool = False):
        expression = (
            Q(
                assigned_room_post__room__participations__user_id=self.user.id,
            ) & 
            (
                Q(
                    assigned_room_post__room__participations__role=ParticipationRoleEnum.host,
                ) | 
                Q(
                    author_id=self.user.id,
                )
            )
        )
        return self.model.filter(expression)

    async def validate_assigned_room_post_id(self, value: int):
        assigned_room_post, _ = await self.room_post_service.retrieve(id=value)

        if not assigned_room_post:
            return None, "Incorrect post id."
        if not assigned_room_post.type == RoomPostType.homework:
            return None, "Can't assign to material."
        if await assigned_room_post.assignments.filter(author=self.user).exists():
            return None, "Homework is already assigned by this user."

        await assigned_room_post.fetch_related('room', 'room__participations')
        participation = await assigned_room_post.room.participations.filter(user=self.user).first()

        if not participation:
            return None, "You are not participating in this room."
        if participation.role in Participation.MODERATOR_ROLES:
            return None, "Teacher's can not assign homeworks."
        return True, None

    async def _check_assignment(
        self,
        assignment: HomeworkAssignment,
    ) -> tuple[bool, Union[str, None]]:
        if not assignment:
            return False, "Invalid assignment."
        if self._check_is_status_restricted(assignment):
            return False, "Can't change assignment now."
        if not await self.user.participations.filter(
            Q(room=assignment.assigned_room_post.room) & (
                Q(role=ParticipationRoleEnum.host) | Q(role=ParticipationRoleEnum.moderator)
            )
        ).exists():
            return False, "You have no permission to do that"
        return True, None

    async def change_assignment_status(
        self,
        assignment_id: int,
        changes_schema: HomeworkAssignmentRequestChangesSchema,
        status: str,
    ) -> tuple[HomeworkAssignment, Union[dict[str, str], None]]:
        assignment, _ = await self.retrieve(
            id=assignment_id,
            _fetch_related=[
                'assigned_room_post',
                'assigned_room_post__room',
            ],
        )

        is_valid, error = await self._check_assignment(assignment)

        if not is_valid:
            return None, error
        
        for field, value in changes_schema.dict().items():
            setattr(assignment, field, value)
        assignment.status = status
        await assignment.save()

        return assignment, None

    request_changes = partialmethod(
        change_assignment_status,
        status=HomeWorkAssignmentStatus.request_changes,
    )
    mark_as_done = partialmethod(
        change_assignment_status,
        status=HomeWorkAssignmentStatus.done,
    )
