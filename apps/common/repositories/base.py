from abc import ABC
from typing import (
    Any,
    Callable,
    Union,
)

import sqlalchemy
from sqlalchemy import (
    func,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession

from apps.common.config import config
from apps.common.database import (
    async_session,
    test_session,
)
from apps.common.models.base import BaseDBModel


class AbstractBaseRepository(ABC):
    _model: BaseDBModel = NotImplemented
    _session_factory: Callable = async_session

    def get_session(self) -> AsyncSession:
        return self._session_factory()

    # TODO: typehints
    async def get_scalar(self, statement):
        """Returns scalar value of statement query."""
        async with self.get_session() as session:
            result = await session.execute(statement)
            return result.scalar()

    def __init__(self) -> None:
        test_mode = config
        if test_mode:
            self._session_factory = test_session


class ReadOnlyRepository(AbstractBaseRepository):
    default_ordering: list[str] = ('id',)

    def _get_column_recursive(self, string: str):
        fields = string.split('.')
        column = getattr(self._model, fields.pop(0))

        for field in fields:
            column = getattr(column, field)
        return column

    def _get_ordering_fields(
        self,
        ordering_strings: list[str],
    ) -> list[sqlalchemy.Column]:
        """Returns list of sqlalchemy columns to perform ordering."""
        columns_list: list[sqlalchemy.Column] = []

        for string in ordering_strings:
            if string.startswith('-'):
                column = self._get_column_recursive(string[1:])
                columns_list.append(column.desc())
                continue
            columns_list.append(self._get_column_recursive(string))
        return columns_list

    # TODO: typehints
    async def _order_query(self, query, ordering: list[str]):
        if ordering:
            ordering_fields = self._get_ordering_fields(ordering)
            return query.order_by(*ordering_fields)
        return query

    async def fetch(
        self,
        ordering: list[str] = None,
        offset: int = 0,
        limit: int = None,
        **filters,
    ) -> list[BaseDBModel]:
        """Fetch list of object with the specific criteria."""
        if not ordering:
            ordering = self.default_ordering

        statement = await self._order_query(
            query=select(self._model).filter_by(**filters),
            ordering=ordering,
        )
        statement = statement.offset(offset)

        if limit:
            statement = statement.limit()

        async with self.get_session() as session:
            result = await session.execute(statement=statement)
            return [obj for obj in result.scalars()]

    async def retrieve(
        self,
        ordering: list[str] = None,
        **filters,
    ) -> Union[BaseDBModel, None]:
        if not ordering:
            ordering = self.default_ordering

        async with self.get_session() as session:
            statement = await self._order_query(
                query=select(self._model).filter_by(**filters),
                ordering=ordering,
            )
            return (await session.execute(statement)).scalars().first()

    async def exists(self, **filters) -> bool:
        return await self.count(**filters) > 0

    async def count(self, **filters) -> int:
        statement = select(func.count(self._model.id)).filter_by(**filters)

        async with self.get_session() as session:
            result = await session.execute(statement=statement)
            return result.scalar()

    async def refresh(self, obj: BaseDBModel) -> BaseDBModel:
        """Refreshes object and returns actual version from database."""
        return await self.retrieve(id=obj.id)


class CreateRepository(AbstractBaseRepository):
    async def create(self, **kwargs) -> BaseDBModel:
        created_object = self._model(**kwargs)

        async with self.get_session() as session:
            session.add(created_object)
            await session.commit()
            return created_object

    async def get_or_create(self, **defaults) -> tuple[BaseDBModel, bool]:
        created = False

        async with self.get_session() as session:
            instance = await session.execute(
                select(self._model).filter_by(**defaults),
            )
            await session.commit()

        if not instance:
            instance = await self.create(**defaults)
            created = True
        return instance, created


class UpdateRepository(AbstractBaseRepository):
    async def update(self, values: dict[str, Any], **filters) -> int:
        """Updates filtered queryset with provided values."""
        statement = update(self._model).filter_by(**filters).values(**values)

        async with self.get_session() as session:
            result = await session.execute(statement)
            await session.commit()
            return result.rowcount


class CreateUpdateRepository(CreateRepository, UpdateRepository):
    pass


class CRUDRepository(
    CreateRepository,
    UpdateRepository,
    ReadOnlyRepository,
    # DeleteRepository,
):
    async def update_object(self, obj: BaseDBModel, **values) -> BaseDBModel:
        """Updates specific object with values."""
        await self.update(values=values, id=obj.id)
        return await self.refresh(obj=obj)

    async def update_and_return(
        self,
        values: dict[str, Any],
        ordering: list[str] = None,
        **filters,
    ) -> BaseDBModel:
        """Updates first object matching provided filters and returns it."""
        updated_rows = await self.update(values=values, **filters)

        if not ordering:
            ordering = self.default_ordering

        if updated_rows:
            return await self.retrieve(ordering=ordering, **filters)
