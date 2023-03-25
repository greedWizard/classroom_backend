from typing import (
    Iterable,
    Optional,
)

from sqlalchemy import (
    func,
    select,
    update,
)

from core.apps.classroom.models.topics import Topic
from core.common.repositories.base import CRUDRepository


class TopicRepository(CRUDRepository):
    _model: type[Topic] = Topic

    async def _displace_orders(self, room_id: int):
        from_table = select(
            self._model.id,
            func.row_number().over(order_by=self._model.order.asc()).label('row_number'),
        ).filter(self._model.room_id == room_id)

        statement = update(self._model).values(order=from_table.c.row_number - 1).filter(
            self._model.id == from_table.c.id,
        )

        async with self.get_session() as session:
            await session.execute(statement)
            await session.commit()

    async def delete_and_displace_orders(self, instances: Iterable[_model]):
        async with self.get_session() as session:
            for instance in instances:
                await self._displace_orders(instance.room_id)
                session.delete(instance)
            await session.commit()

    async def update_next_topics(
        self,
        room_id: int,
        order: int,
    ) -> None:
        statement = update(self._model).filter(
            self._model.order >= order,
            self._model.room_id == room_id,
        ).values(order=self._model.order + 1)

        async with self.get_session() as session:
            await session.execute(statement)
            await session.commit()

    async def update_with_order(
        self,
        topic_id: int,
        title: str,
        order: int,
        join: Optional[list[str]] = None,
    ) -> _model:
        current_topic = await self.retrieve(id=topic_id, join=join)

        if current_topic.order != order:
            await self.update_next_topics(
                room_id=current_topic.room_id,
                order=order,
            )

        async with self.get_session() as session:
            current_topic.title = title
            current_topic.order = order

            session.add(current_topic)
            await session.commit()

        return current_topic

    async def fetch_for_room(
        self,
        room_id: int,
        limit: Optional[int] = None,
        offset: int = 0,
        search: str = '',
    ) -> list[_model]:
        fetch_statement = await self._fetch_statement(
            limit=limit,
            offset=offset,
        )

        fetch_statement = fetch_statement.filter(
            self._model.room_id == room_id,
        ).order_by(self._model.order.asc())

        if search:
            fetch_statement = fetch_statement.filter(
                self._model.title.ilike(f'%{search}%'),
            )

        async with self.get_session() as session:
            result = await session.execute(fetch_statement)
            return result.scalars().all()
