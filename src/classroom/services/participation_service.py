from typing import Dict
import uuid

from tortoise.expressions import Q

from classroom.constants import ParticipationRoleEnum
from classroom.models import Participation, Room

from common.services.author import AuthorMixin
from common.services.base import CRUDService

from user.models import User


class ParticipationService(AuthorMixin, CRUDService):
    model = Participation
    room_model = Room

    def __init__(self, user: User, *args, **kwargs) -> None:
        self.user = user
        super().__init__(user, *args, **kwargs)

    async def get_queryset(self, management: bool = False):
        qs = await super().get_queryset(management)
        room_ids = await self.room_model.filter(participations__user_id=self.user.id)\
            .distinct().values_list('id', flat=True)
        return qs.filter(room_id__in=room_ids).distinct()

    async def validate_join_slug(self, value: str):
        if not await self.room_model.filter(join_slug=value).exists():
            return False, 'This room does not exist.'
        return True, None

    async def is_user_participating(
        self,
        user_id: int,
        room_id: int,
        join_slug: str = None,
    ):
        return await self.model.filter(
            Q(user_id=user_id) & (Q(
                room_id=room_id,
            ) | Q(
                room__join_slug=join_slug
            )),
        ).exists()

    async def can_moderate_room(
        self,
        room_id: int,
        user_id: int
    ):
        participation, _ = await self.retrieve(
            _fetch_related=['room', 'user'],
            room_id=room_id,
            user_id=user_id,
        )

        if not participation:
            return False

        return participation.can_moderate_room()

    async def validate_user_id(self, value: int):
        join_slug = self.current_action_attributes.get('join_slug')
        room_id = self.current_action_attributes.get('room_id')
        if await self.is_user_participating(
            self.current_action_attributes.get('user_id'), room_id, join_slug
        ):
            return False, 'User is already in this room.'
        return True, None

    async def validate(self, attrs: Dict) -> Dict:
        join_slug = self.current_action_attributes.get('join_slug')

        if 'join_slug' in self.current_action_attributes and not \
            'room_id' in self.current_action_attributes:
            attrs['room_id'] = (await self.room_model.filter(join_slug=join_slug).first()).id
        attrs['role'] = attrs.get('role') or ParticipationRoleEnum.participant
        return await super().validate(attrs)
