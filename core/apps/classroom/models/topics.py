import sqlalchemy as sa
from sqlalchemy.orm import (
    backref,
    relationship,
)

from core.common.models.base import BaseDBModel
from core.common.models.mixins import AuthorAbstract


class Topic(BaseDBModel, AuthorAbstract):
    __tablename__ = 'topics'

    title = sa.Column(sa.String(100), nullable=False)
    order = sa.Column(sa.Integer, default=0)

    room_id: int = sa.Column(
        sa.Integer,
        sa.ForeignKey('rooms.id', ondelete='CASCADE'),
        nullable=False,
    )
    room = relationship(
        'Room',
        backref=backref(
            name='topics',
            uselist=True,
        ),
    )

    def __str__(self) -> str:
        return f'Lesson topic #{self.order} "{self.title}"'

    def __repr__(self) -> str:
        return f'<{self}>'
