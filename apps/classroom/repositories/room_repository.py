from apps.classroom.models import Room
from apps.common.repositories.base import CRUDRepository


class RoomRepository(CRUDRepository):
    _model: type[Room] = Room

    async def get_room_by_join_slug(self, join_slug: str):
        return await self.retrieve(join_slug=join_slug)
