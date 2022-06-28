import sqlalchemy as sa
from sqlalchemy.orm import declared_attr


class AuthorAbstract:
    @declared_attr
    def author_id(cls):
        return sa.Column(
            sa.Integer,
            sa.ForeignKey('users.id'),
            nullable=False,
        )

    @declared_attr
    def updated_by_id(cls):
        return sa.Column(
            sa.Integer,
            sa.ForeignKey('users.id'),
            nullable=False,
        )
