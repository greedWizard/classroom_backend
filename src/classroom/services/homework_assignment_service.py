from tortoise.expressions import Q

from classroom.constants import ParticipationRoleEnum, RoomPostType
from classroom.models import HomeworkAssignment, Participation, Room
from classroom.services.room_post_service import RoomPostService

from core.config import config
from core.services.author import AuthorMixin
from core.services.base import CRUDService


class HomeworkAssignmentService(AuthorMixin, CRUDService):
    model = HomeworkAssignment

    @property
    def room_post_service(self):
        return RoomPostService(self.user)

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
        assigned_room_post, errors = await self.room_post_service.retrieve(id=value)

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