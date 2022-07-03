from functools import partialmethod
from typing import Union

from tortoise.expressions import Q

from apps.classroom.constants import (
    ASSIGNMENT_AUTHOR,
    ASSIGNMENT_STATUS_MUTATIONS,
    ASSIGNMENTS_MANAGER,
    HomeWorkAssignmentStatus,
    ParticipationRoleEnum,
    RoomPostType,
)
from apps.classroom.models import (
    HomeworkAssignment,
    Participation,
    RoomPost,
)
from apps.classroom.repositories.assignment import HomeworkAssignmentRepository
from apps.classroom.repositories.participation_repository import ParticipationRepository
from apps.classroom.repositories.post_repository import RoomPostRepository
from apps.classroom.repositories.room_repository import RoomRepository
from apps.classroom.schemas import HomeworkAssignmentRequestChangesSchema
from apps.common.services.author import AuthorMixin
from apps.common.services.base import CRUDService, CreateSchema
from apps.common.services.decorators import action


class AssignmentService(AuthorMixin, CRUDService):
    _repository: HomeworkAssignmentRepository = HomeworkAssignmentRepository()
    _room_repository: RoomRepository = RoomRepository()
    _room_post_repository: RoomPostRepository = RoomPostRepository()
    _participation_repository: ParticipationRepository = ParticipationRepository()

    def _check_is_status_restricted(self, assignment: HomeworkAssignment):
        return assignment.status == HomeWorkAssignmentStatus.done

    async def validate_post_id(self, value: int):
        assigned_post = await self._room_post_repository.retrieve(id=value)

        if not assigned_post:
            return None, 'Incorrect post id.'
        if assigned_post.type != RoomPostType.homework:
            return None, "Can't assign to material."

        if await self._repository.count(
            author_id=self.user.id,
            post_id=assigned_post.id,
        ):
            return None, 'Homework is already assigned by this user.'

        participation: Participation = await self._participation_repository.retrieve(
            user_id=self.user.id,
            room_id=assigned_post.room_id,
        )

        if not participation:
            return None, 'You are not participating in this room.'
        if not participation.can_assign_homeworks:
            return None, "You can't assign the homework."
        return True, None

    @action
    async def fetch_post_assignments(
        self,
        post_id: int,
        **extra_filters,
    ) -> tuple[HomeworkAssignment, Union[dict[str, str], None]]:
        post: RoomPost = await self._room_post_repository.retrieve(
            join=['assignments', 'assignments.author', 'assignments.attachments'],
            id=post_id,
        )
        participation: Participation = await self._participation_repository.retrieve(
            room_id=post.room_id,
            user_id=self.user.id,
        )

        if not participation:
            return None, { 'error': 'You are not allowed to do that'}
        if not participation.can_manage_assignments:
            return None, { 'error': 'You are not allowed to do that'}
        return post.assignments, None

    @action
    async def fetch_room_assignments(self, room_id: int, **filters):
        participation: Participation = await self._participation_repository.retrieve(
            room_id=room_id,
            user_id=self.user.id,
        )
        is_moderator = participation.can_manage_assignments
        join = ['author', 'attachments']

        if not participation and not is_moderator:
            return None, { 'error': 'You are not allowed to do that.' }
        if is_moderator:
            return await self._repository.fetch_by_room_id(
                room_id=room_id,
                join=join,
            ), None
        return await self._repository.fetch_by_room_id(
            join=join,
            room_id=room_id,
            author_id=self.user.id,
        ), None


    async def _check_assignment_rights(
        self,
        assignment: HomeworkAssignment,
        status: str,
    ) -> tuple[bool, Union[str, None]]:
        participation: Participation = await self._participation_repository.retrieve(
            user_id=self.user.id,
            room_id=assignment.post.room_id,
        )

        is_moderator = False

        try:
            is_moderator = participation.can_manage_assignments
        except AttributeError:
            pass

        is_author = assignment.post.author_id == self.user.id
        current_status = assignment.status
        status_mutations = []


        if is_author:
            status_mutations = ASSIGNMENT_STATUS_MUTATIONS.get(
                current_status,
                {},
            ).get(ASSIGNMENT_AUTHOR, [])
        elif is_moderator:
            status_mutations = ASSIGNMENT_STATUS_MUTATIONS.get(
                current_status,
                {},
            ).get(ASSIGNMENTS_MANAGER, [])

        # raise Exception(current_status, status_mutations)
        if status in status_mutations:
            return True, None
        return False, f"Can't change status from '{current_status}' to '{status}'."

    async def change_assignment_status(
        self,
        assignment_id: int,
        status: str,
        changes_schema: HomeworkAssignmentRequestChangesSchema = None,
    ) -> tuple[HomeworkAssignment, Union[dict[str, str], None]]:

        assignment = await self._repository.retrieve(
            id=assignment_id,
            join=['post'],
        )

        is_valid, error = await self._check_assignment_rights(assignment, status)

        if not is_valid:
            return None, error

        changes_dict = changes_schema.dict() if changes_schema else {}
        assignment = await self._repository.update_and_return(
            values={
                'status': status,
                **changes_dict,
            },
            join=['post', 'author', 'attachments'],
        )

        return assignment, None

    @action
    async def retrieve_detail(self, id: int):
        assignment: HomeworkAssignment = await self._repository.retrieve(
            join=['attachments', 'author', 'post'],
            id=id,
        )
        participation: Participation = await self._participation_repository.retrieve(
            user_id=self.user.id,
            room_id=assignment.post.room_id,
        )
        if not participation.can_manage_assignments and \
            assignment.author_id != self.user.id:
            return None, { 'error': 'You are not allowed to do that.'}
        return assignment, None

    @action
    async def retrieve_user_assignment_for_post(
        self,
        post_id: int,
    ) -> HomeworkAssignment:
        return await self._repository.retrieve(
            join=['author', 'attachments'],
            author_id=self.user.id,
            post_id=post_id,
        )

    request_changes = partialmethod(
        change_assignment_status,
        status=HomeWorkAssignmentStatus.request_changes,
    )
    mark_as_done = partialmethod(
        change_assignment_status,
        status=HomeWorkAssignmentStatus.done,
    )
    reassign = partialmethod(
        change_assignment_status,
        status=HomeWorkAssignmentStatus.assigned,
    )
