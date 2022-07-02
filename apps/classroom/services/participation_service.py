from typing import Dict

from apps.classroom.constants import ParticipationRoleEnum
from apps.classroom.repositories.participation_repository import ParticipationRepository
from apps.classroom.repositories.room_repository import RoomRepository
from apps.classroom.schemas.participations import ParticipationSuccessSchema
from apps.common.services.author import AuthorMixin
from apps.common.services.base import CRUDService
from apps.common.services.decorators import action
from apps.user.models import User


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
                join_slug=join_slug
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
