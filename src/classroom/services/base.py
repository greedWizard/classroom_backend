from tortoise.expressions import Q

from classroom.constants import ParticipationRoleEnum
from classroom.models import Participation, Room

from core.config import config
from core.services.author import AuthorMixin
from core.services.base import CRUDService



class AbstractRoomPostService(AuthorMixin, CRUDService):
    room_model = Room
    participation_model = Participation

    async def get_queryset(self, management: bool = False):
        expression = Q(room__participations__user_id=self.user.id)

        if management:
            expression &= (
                Q(room__participations__role=ParticipationRoleEnum.host) | Q(
                    room__participations__role=ParticipationRoleEnum.moderator,
                )
            )

        room_posts_ids = await self.model.filter(expression).distinct().values_list('id', flat=True)
        return self.model.filter(id__in=room_posts_ids).distinct()
    
    async def _validate_moderation(self, room_id: int):
        return await self.participation_model.is_user_moderator(self.user, room_id)

    async def validate_description(self, value: str):
        if not value:
            return True, None
        if len(value) > config.DESCRIPTION_MAX_LENGTH:
            return False, f'Description should be less than {config.TITLE_MAX_LENGTH}' \
                                                'characters.'
        return True, None

    async def validate_title(self, value: str):
        if not value:
            return False, 'This field is required'
        if len(value) > config.TITLE_MAX_LENGTH:
            return False, f'Title should be less than {config.TITLE_MAX_LENGTH} characters.'
        return True, None

    async def validate_room_id(self, value: int):
        if not await self._validate_moderation(value):
            return False, 'You can not moderate this room.'
        return True, None
