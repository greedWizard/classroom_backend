from scheduler.tasks.classroom import notify_room_post_created

from apps.classroom.constants import ParticipationRoleEnum
from apps.classroom.models import RoomPost
from apps.classroom.schemas import RoomPostEmailNotificationSchema
from apps.classroom.services.base import AbstractRoomPostService
from common.config import config
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
        email_subject = RoomPostEmailNotificationSchema.from_orm(room_post)
        email_subject.subject_link = config.FRONTEND_ROOM_POST_URL.format(
            room_post_id=room_post.id,
            room_id=room_post.room_id,
        )

        if room_post:
            notify_room_post_created(
                targets=emails,
                room_post=email_subject,
            )

    @action
    async def create(self, *args, **kwargs):
        room_post, errors = await super().create(
            *args,
            fetch_related=['author', 'room', 'room__author'],
            **kwargs,
        )

        if room_post:
            await self._notify_room_post_create(room_post)
        return room_post, errors
