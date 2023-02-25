from core.apps.classroom.models import RoomPost
from core.common.repositories.base import CRUDRepository


class RoomPostRepository(CRUDRepository):
    _model: type[RoomPost] = RoomPost

    async def search_fetch(
        self,
        ordering: list[str] = None,
        join: list[str] = None,
        offset: int = None,
        limit: int = None,
        search: str = '',
        **filters,
    ):
        statement = await self._fetch_statement(
            ordering,
            join,
            limit=limit,
            offset=offset,
            **filters,
        )

        statement = statement.filter(
            self._model.title.ilike(f'%{search}%'),
        )

        async with self.get_session() as session:
            result = await session.execute(statement)
            return result.unique().scalars().all()
