from typing import Dict
import uuid

from tortoise.expressions import Q

from classroom.constants import ParticipationRoleEnum
from classroom.models import RoomPost, Participation, Room

from core.services.author import AuthorMixin
from core.services.base import CRUDService
from core.services.decorators import action

from user.models import User


class AbstractRoomPostService(AuthorMixin, CRUDService):
    room_model = Room
    participation_model = Participation

    async def get_queryset(self, for_delete=False):
        expression = Q(room__participations__user_id=self.user.id)

        if for_delete:
            expression &= Q(room__participations__role=ParticipationRoleEnum.host)

        room_posts_ids = await self.model.filter(expression).distinct().values_list('id', flat=True)
        return self.model.filter(id__in=room_posts_ids).distinct()
    
    async def _validate_moderation(self, room_id: int):
        return await self.participation_model.is_user_moderator(self.user, room_id)

    async def validate_title(self, value: str):
        if not value:
            return False, 'This field is required'
        return True, None

    async def validate_room_id(self, value: int):
        if not await self._validate_moderation(value):
            return False, 'You can not moderate this room.'
        return True, None
