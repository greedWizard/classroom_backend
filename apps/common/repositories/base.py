from abc import ABC
from dataclasses import field
from typing import (
    Any,
    NewType,
)


# TODO: вписать модель
DataBaseModel = NewType('DatabaseModel', Any)


class AbstractBaseRepository(ABC):
    _model: DataBaseModel = NotImplemented()


class ReadOnlyRepository(AbstractBaseRepository):
    default_ordering: list[str] = field(default_factory=lambda: ['id'])

    def fetch(
        self,
        prefetch_fields: list[str],
        ordering: list[str] = None,
        **filters,
    ):
        """Fetch list of object with the specific criteria."""
        if not ordering:
            ordering = self.default_ordering

        return (
            self._model.filter(**filters)
            .prefetch_related(*prefetch_fields)
            .order_by(*ordering)
            .all()
        )

    def retrieve(
        self,
        prefetch_fields: list[str],
        **filters,
    ):
        """Retrieve first object with matching criteria."""
        if not ordering:
            ordering = self.default_ordering

        self._model.filter(**filters).prefetch_related(*prefetch_fields).order_by(
            *ordering
        ).first()
