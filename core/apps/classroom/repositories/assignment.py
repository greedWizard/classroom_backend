from core.apps.classroom.models import (
    HomeworkAssignment,
    RoomPost,
)
from core.common.repositories.base import CRUDRepository


class HomeworkAssignmentRepository(CRUDRepository):
    _model: type[HomeworkAssignment] = HomeworkAssignment
    _post_model: type[RoomPost] = RoomPost

    async def fetch_by_post_id(
        self,
        post_id: int,
        join: list[str] = None,
        ordering: list[str] = None,
        offset: int = 0,
        limit: int = 0,
        **extra_filters,
    ) -> list[HomeworkAssignment]:
        statement = await self._fetch_statement(
            ordering=ordering,
            join=join,
            offset=offset,
            limit=limit,
            **extra_filters,
        )
        statement = statement.join(self._model.post).filter(
            self._model.post_id == post_id,
        )

        async with self.get_session() as session:
            result = await session.execute(statement)
            return result.unique().scalars().all()

    async def fetch_by_room_id(
        self,
        room_id: int,
        join: list[str] = None,
        ordering: list[str] = None,
        offset: int = 0,
        limit: int = 0,
        **extra_filters,
    ) -> list[HomeworkAssignment]:
        statement = await self._fetch_statement(
            ordering=ordering,
            join=join,
            offset=offset,
            limit=limit,
            **extra_filters,
        )
        statement = (
            statement.join(self._model.post)
            .filter(
                self._post_model.room_id == room_id,
            )
            .group_by(self._model)
        )

        async with self.get_session() as session:
            result = await session.execute(statement)
            return result.unique().scalars().all()
