import sqlalchemy as sa
from sqlalchemy.orm import (
    backref,
    declared_attr,
    relationship,
)


class AuthorAbstract:
    @declared_attr
    def author_id(cls):
        return sa.Column(
            sa.Integer,
            sa.ForeignKey('users.id'),
            nullable=False,
        )

    @declared_attr
    def author(cls):
        return relationship(
            'User',
            backref=backref(
                f'created_{cls.__tablename__}',
                uselist=True,
            ),
            foreign_keys=[cls.author_id],
        )

    @declared_attr
    def updated_by_id(cls):
        def default_updated_by(context):
            return context.get_current_parameters()['author_id']

        return sa.Column(
            sa.Integer,
            sa.ForeignKey('users.id'),
            nullable=False,
            default=default_updated_by,
        )

    @declared_attr
    def updated_by(cls):
        return relationship(
            'User',
            backref=backref(
                f'updated_{cls.__tablename__}',
                uselist=True,
            ),
            foreign_keys=[cls.updated_by_id],
        )
