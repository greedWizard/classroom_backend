from sqlalchemy import select

from apps.classroom.models import HomeworkAssignment, RoomPost
from apps.common.repositories.base import CRUDRepository


class HomeworkAssignmentRepository(CRUDRepository):
    _model: type[HomeworkAssignment] = HomeworkAssignment
    _post_model: type[RoomPost] = RoomPost

    async def fetch_by_room_id(
        self,
        room_id: int,
        join: list[str] = None,
        ordering: list[str] = None,
        offset: int = 0,
        limit: int = 0,
        **extra_filters,
    ):
        statement = await self._fetch_statement(
            ordering=ordering,
            join=join,
            offset=offset,
            limit=limit,
            **extra_filters,
        )
        statement = statement.join(self._model.post).filter(
            self._post_model.room_id == room_id,
        ).group_by(self._model)

        async with self.get_session() as session:
            result = await session.execute(statement)
            return result.unique().scalars().all()