import sqlalchemy as sa
from sqlalchemy.orm import (
    backref,
    relationship,
    validates,
)

from core.apps.classroom.constants import HomeWorkAssignmentStatus
from core.apps.classroom.models.room_posts import RoomPost
from core.common.models.base import BaseDBModel
from core.common.models.mixins import AuthorAbstract


class HomeworkAssignment(BaseDBModel, AuthorAbstract):
    __tablename__ = 'assignments'
    __table_args__ = (sa.UniqueConstraint('post_id', 'author_id'),)

    status = sa.Column(
        sa.Enum(HomeWorkAssignmentStatus),
        default=HomeWorkAssignmentStatus.assigned,
    )
    rate = sa.Column(sa.Integer)
    comment = sa.Column(sa.Text)

    # relations
    post_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('posts.id', ondelete='CASCADE'),
        nullable=False,
    )
    post: RoomPost = relationship(
        'RoomPost',
        backref=backref(
            name='assignments',
            uselist=True,
        ),
    )

    attachments = relationship(
        'Attachment',
        backref=backref(
            name='assignment',
        ),
        uselist=True,
    )

    @validates('rate')
    def validate_rate_range(self, key, rate):
        if not 0 <= rate <= 5:
            raise ValueError('Rate should be in a range {0, 5}')
        return rate

    def __str__(self) -> str:
        return f'HomeworkAssignment {self.created_at} by {self.author_id}'

    def __repr__(self) -> str:
        return f'<{self}>'

    @property
    def status_assigned(self):
        return self.status == HomeWorkAssignmentStatus.assigned

    @property
    def status_done(self):
        return self.status == HomeWorkAssignmentStatus.done

    @property
    def status_request_changes(self):
        return self.status == HomeWorkAssignmentStatus.request_changes
