from scheduler.tasks.classroom import notify_room_post_created

from apps.classroom.constants import ParticipationRoleEnum
from apps.classroom.models import RoomPost
from apps.classroom.schemas import RoomPostListItemSchema
from apps.classroom.services.base import AbstractRoomPostService
from common.services.decorators import action


class RoomPostService(AbstractRoomPostService):
    model = RoomPost

    async def _notify_room_post_create(self, room_post: RoomPost):
        emails = await room_post.room.participations.filter(
            role=ParticipationRoleEnum.participant,
        ).values_list(
            'user__email',
            flat=True,
        )

        if room_post:
            notify_room_post_created(
                targets=[emails],
                room_post=RoomPostListItemSchema.from_orm(room_post),
            )

    @action
    async def create(self, *args, **kwargs):
        room_post, errors = await super().create(
            *args,
            fetch_related=['author', 'room'],
            **kwargs,
        )

        if room_post:
            await self._notify_room_post_create(room_post)
        return room_post, errors
