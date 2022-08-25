import uuid

import sqlalchemy as sa
from sqlalchemy.orm import (
    backref,
    relationship,
    validates,
)

from core.apps.classroom.constants import (
    HomeWorkAssignmentStatus,
    ParticipationRoleEnum,
    RoomPostType,
)
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


class Participation(BaseDBModel, AuthorAbstract):
    __tablename__ = 'participations'
    __table_args__ = (sa.UniqueConstraint('user_id', 'room_id'),)

    MODERATOR_ROLES = (
        ParticipationRoleEnum.host,
        ParticipationRoleEnum.moderator,
    )

    role = sa.Column(
        sa.Enum(ParticipationRoleEnum),
        default=ParticipationRoleEnum.participant,
        nullable=False,
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
            name='participations',
            uselist=True,
            passive_deletes=True,
        ),
    )
    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
    user = relationship(
        'User',
        backref=backref(
            name='participations',
            uselist=True,
        ),
        foreign_keys=[user_id],
    )

    @property
    def can_manage_posts(self) -> bool:
        return self.role in Participation.MODERATOR_ROLES

    @property
    def can_examine(self) -> bool:
        return self.role == ParticipationRoleEnum.host

    @property
    def can_assign_homeworks(self) -> bool:
        return self.role == ParticipationRoleEnum.participant

    @property
    def can_remove_participants(self) -> bool:
        return self.role in self.MODERATOR_ROLES

    @property
    def can_refresh_join_slug(self) -> bool:
        return self.role in self.MODERATOR_ROLES

    @property
    def can_delete_room(self) -> bool:
        return self.role == ParticipationRoleEnum.host

    @property
    def can_update_room(self):
        return self.role in self.MODERATOR_ROLES

    @property
    def can_manage_assignments(self):
        return self.role in self.MODERATOR_ROLES

    @property
    def is_moderator(self):
        return self.role in self.MODERATOR_ROLES


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
