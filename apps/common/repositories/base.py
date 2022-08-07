from abc import ABC
from typing import (
    Any,
    Callable,
    Union,
)

import sqlalchemy
from sqlalchemy import (
    delete,
    func,
    select,
    update,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from apps.common.config import config
from apps.common.database import (
    async_session,
    test_session,
)
from apps.common.models.base import BaseDBModel
from apps.common.repositories.exceptions import ObjectAlreadyExistsException


class AbstractBaseRepository(ABC):
    _model: BaseDBModel = NotImplemented
    _session_factory: Callable = async_session
    _integrity_error: Exception = IntegrityError

    def get_session(self) -> AsyncSession:
        return self._session_factory()

    # TODO: typehints
    async def get_scalar(self, statement):
        """Returns scalar value of statement query."""
        async with self.get_session() as session:
            result = await session.execute(statement)
            return result.scalar()

    def __init__(self) -> None:
        test_mode = config.TEST_MODE
        if test_mode:
            self._session_factory = test_session

    @property
    def model_fields(self):
        return self._model.__table__.columns


class ReadOnlyRepository(AbstractBaseRepository):
    default_ordering: list[str] = []

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

    async def _get_join_options_recursive(self, column: str):
        fields = column.split('.')
        option = joinedload(fields.pop(0))

        for nested_field in fields:
            option = option.joinedload(nested_field)
        return option

    async def _join_statement(self, statement, columns: list[str]):
        load_options = [
            await self._get_join_options_recursive(column) for column in columns
        ]
        statement = statement.options(*load_options)
        return statement

    async def _fetch_statement(
        self,
        ordering: list[str] = None,
        join: list[str] = None,
        offset: int = None,
        limit: int = None,
        **filters,
    ):
        statement = select(self._model)

        if not ordering:
            ordering = self.default_ordering
        if join:
            statement = await self._join_statement(
                statement=statement,
                columns=join,
            )

        statement = statement.filter_by(**filters)
        statement = await self._order_query(
            query=statement,
            ordering=ordering,
        )

        if offset:
            statement = statement.offset(offset)
        if limit:
            statement = statement.limit(limit)
        return statement

    async def fetch(
        self,
        ordering: list[str] = None,
        join: list[str] = None,
        offset: int = 0,
        limit: int = None,
        **filters,
    ) -> list[BaseDBModel]:
        """Fetch list of object with the specific criteria."""
        statement = await self._fetch_statement(
            ordering=ordering,
            join=join,
            offset=offset,
            limit=limit,
            **filters,
        )

        async with self.get_session() as session:
            result = await session.execute(statement)
            return result.unique().scalars().all()

    async def retrieve(
        self,
        ordering: list[str] = None,
        join: list[str] = None,
        **filters,
    ) -> Union[BaseDBModel, None]:
        statement = await self._fetch_statement(
            ordering=ordering,
            join=join,
            **filters,
        )

        async with self.get_session() as session:
            return (await session.execute(statement)).scalars().first()

    async def exists(self, **filters) -> bool:
        statement = await self._fetch_statement(**filters)

        async with self.get_session() as session:
            result = await session.execute(statement.exists().select())
            return result.scalar()

    async def count(self, **filters) -> int:
        statement = select(func.count(self._model.id)).filter_by(**filters)

        async with self.get_session() as session:
            result = await session.execute(statement=statement)
            return result.scalar()

    async def refresh(self, obj: BaseDBModel, join: list[str] = None) -> BaseDBModel:
        """Refreshes object and returns actual version from database."""
        if isinstance(obj, self._model):
            return await self.retrieve(id=obj.id, join=join)


class CreateRepository(AbstractBaseRepository):
    async def create(self, join: list[str] = None, **kwargs) -> BaseDBModel:
        created_object = self._model(**kwargs)

        async with self.get_session() as session:
            session.add(created_object)
            try:
                await session.commit()
            except self._integrity_error as e:
                raise ObjectAlreadyExistsException(e)

            if join:
                return await self.retrieve(id=created_object.id, join=join)
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


class DeleteRepository(AbstractBaseRepository):
    async def delete(self, **filters):
        statement = delete(self._model).filter_by(**filters)

        async with self.get_session() as session:
            result = await session.execute(statement)
            await session.commit()
            return result.rowcount


class CRUDRepository(
    CreateRepository,
    UpdateRepository,
    ReadOnlyRepository,
    DeleteRepository,
):
    async def update_object(self, obj: BaseDBModel, **values) -> BaseDBModel:
        """Updates specific object with values."""
        await self.update(values=values, id=obj.id)
        return await self.refresh(obj=obj)

    async def update_and_return_single(
        self,
        values: dict[str, Any],
        join: list[str] = None,
        **filters,
    ) -> BaseDBModel:
        """Updates first object matching provided filters and returns it."""
        updated_rows = await self.update(values=values, **filters)

        if updated_rows:
            return await self.retrieve(join=join, **filters)
