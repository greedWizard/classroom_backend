from typing import (
    Any,
    Dict,
)

from core.apps.classroom.constants import ParticipationRoleEnum
from core.apps.classroom.repositories.participation_repository import ParticipationRepository
from core.apps.classroom.repositories.room_repository import RoomRepository
from core.apps.classroom.schemas.participations import ParticipationSuccessSchema
from core.apps.users.models import User
from core.common.services.author import AuthorMixin
from core.common.services.base import CRUDService
from core.common.services.decorators import action


class ParticipationService(AuthorMixin, CRUDService):
    _repository: ParticipationRepository = ParticipationRepository()
    _room_repository: RoomRepository = RoomRepository()
    schema_map = {
        'create': ParticipationSuccessSchema,
    }

    def __init__(self, user: User, *args, **kwargs) -> None:
        self.user = user
        super().__init__(user, *args, **kwargs)

    async def validate_join_slug(self, value: str):
        if not await self._room_repository.exists(
            join_slug=value,
        ):
            return False, 'This room does not exist.'
        return True, None

    async def validate_user_id(self, value: int):
        room_id = self.current_action_attributes.get('room_id')
        user_id = value

        if await self._repository.exists(room_id=room_id, user_id=user_id):
            return False, 'User is already in this room.'
        return True, None

    async def validate(self, attrs: Dict) -> Dict:
        attrs['role'] = attrs.get('role') or ParticipationRoleEnum.participant

        if 'join_slug' in attrs:
            join_slug = attrs.pop('join_slug')
            room = await self._room_repository.get_room_by_join_slug(
                join_slug=join_slug,
            )
            attrs['room_id'] = room.id

        return await super().validate(attrs)

    @action
    async def remove_user_from_room(self, user_id: int, room_id: int):
        participation, _ = await self.retrieve(
            room_id=room_id,
            user_id=self.user.id,
        )
        errors = []

        if not participation:
            return False, {'error': 'Not Found'}
        if not participation.can_remove_participants:
            errors.append({'room_id': 'Permission denied'})
        if (
            participation.role == ParticipationRoleEnum.host
            and participation.user_id == user_id
        ):
            errors.append({'user_id': "Can't remove a room host."})
        if errors:
            return False, errors
        await self.model.filter(user_id=user_id, room_id=room_id).delete()
        return True, None

    @action
    async def fetch_for_user(
        self,
        _ordering: dict[str, Any] = None,
        **filters,
    ):
        return await self.fetch(
            _ordering=_ordering,
            join=['room', 'room.author', 'room.participations'],
            user_id=self.user.id,
            **filters,
        )

    @action
    async def fetch_by_room(
        self,
        room_id: int,
        _ordering: list = ...,
        join: list[str] = None,
        **filters,
    ):
        if await self._repository.count(room_id=room_id, user_id=self.user.id):
            return await super().fetch(_ordering, join, room_id=room_id, **filters)
        return None, {'error': 'Access denied.'}
