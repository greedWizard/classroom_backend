import uuid
from typing import Dict

from tortoise.expressions import Q
from tortoise.transactions import atomic

from apps.classroom.constants import ParticipationRoleEnum
from apps.classroom.models import Room
from apps.classroom.schemas import ParticipationCreateSchema
from apps.classroom.services.participation_service import ParticipationService
from apps.user.models import User
from common.services.author import AuthorMixin
from common.services.base import CRUDService
from common.services.decorators import action


class RoomService(AuthorMixin, CRUDService):
    model = Room

    def __init__(self, user: User, *args, **kwargs) -> None:
        self.user = user
        super().__init__(user, *args, **kwargs)

    async def get_queryset(self, management: bool = False):
        expression = Q(participations__user_id=self.user.id)

        if management:
            expression &= Q(participations__role=ParticipationRoleEnum.host) | Q(
                participations__role=ParticipationRoleEnum.moderator,
            )
        return self.model.filter(expression).distinct()

    def generate_join_slug(self):
        return uuid.uuid4().hex

    @property
    def participation_service(self):
        return ParticipationService(user=self.user)

    async def validate(self, attrs: Dict) -> Dict:
        attrs = await super().validate(attrs)

        attrs['join_slug'] = uuid.uuid4().hex
        return attrs

    @action
    @atomic()
    async def create(self, createSchema, exclude_unset: bool = False):
        created_room, errors = await super().create(createSchema, exclude_unset)

        if not errors:
            await self.participation_service.create(
                ParticipationCreateSchema(
                    user_id=self.user.id,
                    room_id=created_room.id,
                    role=ParticipationRoleEnum.host,
                    author_id=self.user.id,
                ),
            )

        # TODO: логировать создание комнаты
        return created_room, errors

    @action
    async def refresh_join_slug(self, room_id: int) -> Dict:
        """Create or refresh join link."""
        participation, errors = await self.participation_service.retrieve(
            user_id=self.user.id,
            room_id=room_id,
            _fetch_related=['room', 'user'],
        )

        if errors:
            return None, errors
        if not participation.can_moderate_room():
            return {}, 'You are not allowed to perform this operation.'

        room, _ = await self.retrieve(id=room_id)
        room.join_slug = self.generate_join_slug()
        await room.save()

        return room.join_slug, None

    async def _validate_delete(self, deleteSchema):
        if not await self.participation_service.can_moderate_room(
            room_id=self.current_action_attributes.get('id'),
            user_id=self.user.id,
        ):
            return None, 'You can not moderate this room'
        return await super()._validate_delete(deleteSchema)

    async def validate_name(self, value):
        if not value:
            return False, 'This field is required'
        return True, None
