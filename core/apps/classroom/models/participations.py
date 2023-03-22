import sqlalchemy as sa
from sqlalchemy.orm import (
    backref,
    relationship,
)

from core.apps.classroom.constants import ParticipationRoleEnum
from core.common.models.base import BaseDBModel
from core.common.models.mixins import AuthorAbstract


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
