from apps.classroom.models import RoomPost
from apps.classroom.services.base import AbstractRoomPostService
from common.services.decorators import action


class RoomPostService(AbstractRoomPostService):
    model = RoomPost

    @action
    async def create(self, *args, **kwargs):
        room_post, errors = await super().create(*args, **kwargs)

        if room_post:
            pass
        return room_post, errors
