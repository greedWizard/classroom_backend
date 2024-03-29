import uuid
from typing import (
    Dict,
    Union,
)

from pydantic import BaseModel

from core.apps.classroom.constants import ParticipationRoleEnum
from core.apps.classroom.models import Participation
from core.apps.classroom.repositories.participation_repository import ParticipationRepository
from core.apps.classroom.repositories.room_repository import RoomRepository
from core.apps.classroom.schemas import ParticipationCreateSchema
from core.apps.classroom.schemas.rooms import (
    RoomCreateSuccessSchema,
    RoomDetailSchema,
)
from core.apps.localization.utils import translate as _
from core.common.services.author import AuthorMixin
from core.common.services.base import CRUDService
from core.common.services.decorators import action


class RoomService(AuthorMixin, CRUDService):
    _repository: RoomRepository = RoomRepository()
    _participation_repository: ParticipationRepository = ParticipationRepository()

    schema_map: dict[str, BaseModel] = {
        'create': RoomCreateSuccessSchema,
        'retrieve_detailed': RoomDetailSchema,
    }

    def generate_join_slug(self):
        return uuid.uuid4().hex

    async def validate(self, attrs: Dict) -> Dict:
        attrs = await super().validate(attrs)
        attrs['join_slug'] = uuid.uuid4().hex
        return attrs

    @action
    async def create(
        self,
        create_schema,
        exclude_unset: bool = False,
        join: list[str] = None,
    ):
        created_room, errors = await super().create(create_schema, exclude_unset)

        if errors:
            return None, errors

        participations_schema = ParticipationCreateSchema(
            user_id=self.user.id,
            room_id=created_room.id,
            role=ParticipationRoleEnum.host,
            author_id=self.user.id,
        )
        await self._participation_repository.create(
            join=join,
            **participations_schema.dict(),
        )
        return created_room, errors

    @action
    async def refresh_join_slug(self, room_id: int) -> Dict:
        """Create or refresh join link."""
        participation: Participation = await self._participation_repository.retrieve(
            user_id=self.user.id,
            room_id=room_id,
        )

        if not participation:
            return None, _('You are not allowed to perform this operation.')
        if not participation.can_refresh_join_slug:
            return None, _('You are not allowed to perform this operation.')

        room = await self._repository.update_and_return_single(
            values={'join_slug': self.generate_join_slug()},
            id=room_id,
        )
        return room.join_slug, None

    @action
    async def delete(self, **filters):
        room_id = filters.get('id')

        participation: Participation = await self._participation_repository.retrieve(
            user_id=self.user.id,
            room_id=room_id,
        )
        permission_error = _('You are not allowed to do that.')

        if not participation:
            return None, permission_error
        if not participation.can_delete_room:
            return None, permission_error
        deleted_rooms_count = await self._repository.delete(**filters)

        await self._participation_repository.delete(
            room_id=participation.room_id,
        )
        return deleted_rooms_count, None

    async def validate_name(self, value):
        if not value:
            return False, _('This field is required')
        return True, None

    async def update(
        self,
        id: Union[str, None],
        update_schema,
        exclude_unset: bool = True,
        join: list[str] = None,
    ):
        participation: Participation = await self._participation_repository.retrieve(
            room_id=id,
            user_id=self.user.id,
        )

        if participation.can_update_room:
            return await super().update(
                id=id,
                update_schema=update_schema,
                join=join,
                exclude_unset=exclude_unset,
            )
        return None, {'error': _('You are not allowed to do that.')}
