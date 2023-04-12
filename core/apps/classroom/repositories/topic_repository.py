from typing import (
    Iterable,
    Optional,
)

from sqlalchemy import (
    func,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession

from core.apps.classroom.models.topics import Topic
from core.common.repositories.base import CRUDRepository


class TopicRepository(CRUDRepository):
    _model: type[Topic] = Topic

    async def _displace_orders(self, room_id: int, session: AsyncSession):
        statement = select(self._model).where(
            self._model.room_id == room_id,
        ).order_by(
            self._model.order.asc(),
        )
        existing_topics_in_room = (await session.execute(statement)).scalars().all()

        for index, topic in enumerate(existing_topics_in_room, 1):
            topic.order = index

        session.add_all(existing_topics_in_room)

    async def delete_and_displace_orders(self, instances: Iterable[_model]):
        async with self.get_session() as session:
            for instance in instances:
                await session.delete(instance)
                await self._displace_orders(instance.room_id, session=session)
            await session.commit()

    async def update_next_topics(
        self,
        room_id: int,
        order: int,
        session: AsyncSession,
        current_order: Optional[int] = None,
    ) -> None:
        max_order = (
            await session.execute(
                select(func.max(self._model.order)),
            )
        ).scalar()

        if order != max_order:
            statement = update(self._model).filter(
                self._model.order >= order,
                self._model.room_id == room_id,
            ).values(order=self._model.order + 1)
        else:
            statement = update(self._model).filter(
                self._model.order > current_order,
                self._model.room_id == room_id,
            ).values(order=self._model.order - 1)
        await session.execute(statement)

    async def update_with_order(
        self,
        topic_id: int,
        join: Optional[list[str]] = None,
        **update_kwargs,
    ) -> _model:
        order = update_kwargs.get('order')
        current_topic: Topic = await self.retrieve(id=topic_id, join=join)

        async with self.get_session() as session:
            if order is not None and current_topic.order != order:
                await self.update_next_topics(
                    room_id=current_topic.room_id,
                    order=order,
                    session=session,
                    current_order=current_topic.order,
                )

            for field, value in update_kwargs.items():
                setattr(current_topic, field, value)

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
