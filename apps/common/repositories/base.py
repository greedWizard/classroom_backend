from abc import ABC
from dataclasses import field
from typing import Callable

from sqlalchemy import (
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession

from apps.common.config import config
from apps.common.database import (
    async_session,
    DBModel,
    test_session,
)


class AbstractBaseRepository(ABC):
    _model: DBModel = NotImplemented
    _session: AsyncSession
    _session_factory: Callable = async_session

    def get_session(self) -> AsyncSession:
        return self._session_factory()

    # TODO: typehints
    async def get_scalar(self, statement):
        """Returns scalar value of statement query """
        async with self.get_session() as session:
            result = await session.execute(statement)
            return result.scalar()

    def __init__(self) -> None:
        test_mode = config
        if test_mode:
            self._session_factory = test_session


class ReadOnlyRepository(AbstractBaseRepository):
    default_ordering: list[str] = field(default_factory=lambda: ['id'])

    async def fetch(
        self,
        ordering: list[str] = None,
        **filters,
    ) -> list[DBModel]:
        """Fetch list of object with the specific criteria."""
        if not ordering:
            ordering = self.default_ordering

        statement = select(self._model).filter_by(**filters)

        async with self.get_session() as session:
            result = await session.execute(statement=statement)
            return [obj for obj in result.scalars()]

    async def exists(self, **filters) -> bool:
        return await self.count(**filters) > 0

    async def count(self, **filters) -> int:
        statement = select(func.count(self._model.id)).filter_by(**filters)

        async with self.get_session() as session:
            result = await session.execute(statement=statement)
            return result.scalar()


class CreateRepository(AbstractBaseRepository):
    async def create(self, **kwargs) -> DBModel:
        created_object = self._model(**kwargs)

        async with self.get_session() as session:
            session.add(created_object)
            await session.commit()
            return created_object

    async def get_or_create(self, **defaults) -> tuple[DBModel, bool]:
        created = False

        async with self.get_session() as session:
            instance = await session.execute(
                select(self._model).filter_by(**defaults),
            )

        if not instance:
            instance = await self.create(**defaults)
            created = True
        return instance, created


class UpdateRepository(AbstractBaseRepository):
    async def update(self, filters: dict[str, any], **kwargs):
        """Updated filtered queryset with provided kwargs."""


class CreateUpdateRepository(CreateRepository, UpdateRepository):
    pass


class CRUDRepository(
    CreateRepository,
    UpdateRepository,
    ReadOnlyRepository,
    # DeleteRepository,
):
    pass
