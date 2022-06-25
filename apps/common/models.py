import sqlalchemy as sa
from sqlalchemy.orm import relationship

from apps.common.utils import get_current_datetime


class BaseMetaData:
    id = sa.Column(
        sa.Integer,
        primary_key=True,
    )
    created_at = sa.Column(
        sa.DateTime,
        default=get_current_datetime,
    )
    updated_at = sa.Column(
        sa.DateTime,
        default=get_current_datetime,
        onupdate=get_current_datetime,
    )


class AuthorAbstract:
    author = relationship('User')
    author_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('users.id'),
        nullable=False,
    )
    updated_by = relationship('User')
    updated_by_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('users.id'),
        nullable=False,
    )
