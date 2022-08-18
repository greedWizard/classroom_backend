from core.apps.classroom.models import Room
from core.common.repositories.base import CRUDRepository

from sqlalchemy import select


class RoomRepository(CRUDRepository):
    _model: type[Room] = Room

    async def get_room_by_join_slug(self, join_slug: str):
        return await self.retrieve(join_slug=join_slug)

    async def get_by_post(self, post_id: int, join: list[str] = None) -> _model:
        """Returns the room that includes post with that post_id."""
        if not join:
            join = []

        query = select(self._model).filter(self._model.posts.any(id=post_id))
        query = await self._join_statement(query, columns=join)

        async with self.get_session() as session:
            result = await session.execute(query)
            return result.scalar()
