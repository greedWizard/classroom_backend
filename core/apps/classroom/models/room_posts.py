import sqlalchemy as sa
from sqlalchemy.orm import (
    backref,
    relationship,
)

from core.apps.classroom.constants import RoomPostType
from core.common.models.base import BaseDBModel
from core.common.models.mixins import AuthorAbstract


class AttachmentsCountMixin:
    @property
    def attachments_count(self) -> int:
        return len(self.attachments)


class RoomPost(BaseDBModel, AttachmentsCountMixin, AuthorAbstract):
    __tablename__ = 'posts'

    title = sa.Column(sa.String(200), nullable=False)
    description = sa.Column(sa.String(500))
    text = sa.Column(sa.Text())
    deadline_at = sa.Column(sa.DateTime)
    type = sa.Column(
        sa.Enum(RoomPostType),
        default=RoomPostType.material,
    )

    # relations
    room_id: int = sa.Column(
        sa.Integer,
        sa.ForeignKey('rooms.id', ondelete='CASCADE'),
        nullable=False,
    )
    room = relationship(
        'Room',
        backref=backref(
            name='posts',
            uselist=True,
        ),
    )
    attachments = relationship(
        'Attachment',
        backref=backref(
            name='post',
        ),
        uselist=True,
    )
    topic_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('topics.id', ondelete='SET NULL'),
    )
    topic = relationship(
        'Topic',
        backref=backref(
            'posts',
            uselist=True,
        ),
    )

    @property
    def is_assignable(self):
        return self.type == RoomPostType.homework

    @property
    def assignments_count(self):
        return len(self.assignments)

    def __str__(self) -> str:
        return f'"{self.title}" / "{self.description}"'

    def __repr__(self) -> str:
        return f'<RoomPost {str(self)}>'
