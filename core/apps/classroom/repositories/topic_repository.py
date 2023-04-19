from typing import (
    Iterable,
    Optional,
)

from sqlalchemy import (
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

    async def change_orders(
        self,
        room_id: int,
        current_topic: Topic,
        new_order: int,
        session: AsyncSession,
    ) -> None:
        if current_topic.order == new_order:
            return

        available_orders = (
            await session.execute(
                select(self._model.order).filter(self._model.room_id == room_id),
            )
        ).scalars().all()

        if new_order in available_orders:
            await session.execute(
                update(self._model).where(
                    self._model.room_id == room_id,
                    self._model.order == new_order,
                ).values(order=current_topic.order),
            )
        current_topic.order = new_order

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
                await self.change_orders(
                    room_id=current_topic.room_id,
                    session=session,
                    current_topic=current_topic,
                    new_order=order,
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
