import uuid

import sqlalchemy as sa

from core.common.models.base import BaseDBModel
from core.common.models.mixins import AuthorAbstract


class Room(BaseDBModel, AuthorAbstract):
    __tablename__ = 'rooms'

    name = sa.Column(sa.String(100), nullable=False)
    description = sa.Column(sa.String(250))
    join_slug = sa.Column(
        sa.String(256),
        default=lambda: uuid.uuid4().hex,
        unique=True,
    )

    @property
    def participations_count(self):
        return len(self.participations)

    def __str__(self) -> str:
        return f'{self.name[:50]} {self.description}'

    def __repr__(self) -> str:
        return f'<{self.name[:50]} {self.description}>'
