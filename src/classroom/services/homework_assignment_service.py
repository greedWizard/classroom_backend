from tortoise.expressions import Q

from classroom.constants import ParticipationRoleEnum
from classroom.models import HomeworkAssignment, Participation, Room

from core.config import config
from core.services.author import AuthorMixin
from core.services.base import CRUDService


class AbstractRoomPostService(AuthorMixin, CRUDService):
    model = HomeworkAssignment

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
