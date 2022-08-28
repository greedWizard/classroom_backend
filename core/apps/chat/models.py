import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    backref,
    relationship,
)

from core.common.models.base import BaseDBModel
from core.common.models.mixins import AuthorAbstract


DialogsParticipants = sa.Table(
    'dialogs_participants',
    BaseDBModel.metadata,
    sa.Column(
        'user_id',
        sa.Integer(),
        sa.ForeignKey(
            'users.id',
            ondelete='CASCADE',
        ),
        nullable=False,
        primary_key=True,
    ),
    sa.Column(
        'dialog_id',
        sa.Integer(),
        sa.ForeignKey(
            'dialogs.id',
            ondelete='CASCADE',
        ),
        nullable=False,
        primary_key=True,
    ),
)


class Dialog(BaseDBModel, AuthorAbstract):
    __tablename__ = 'dialogs'

    participants = relationship(
        'User',
        secondary=DialogsParticipants,
        backref=backref(
            'dialogs',
            uselist=True,
        ),
    )

    @hybrid_property
    def participants_count(self):
        return len(self.participants)

    @participants_count.expression
    def participants_count(cls):
        return sa.select([
            sa.func.count(DialogsParticipants.c.dialog_id),
        ]).where(DialogsParticipants.c.dialog_id == cls.id).label('participants_count')

    def __str__(self) -> str:
        return f'Dialog #{self.id}'

    def __repr__(self) -> str:
        return f'<{self}>'


class Message(BaseDBModel):
    __tablename__ = 'messages'

    sender_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(
            'users.id',
            ondelete='CASCADE',
        ),
        nullable=False,
    )
    sender = relationship(
        'User',
        backref=backref(
            name='sent_messages',
            uselist=True,
        ),
        foreign_keys=[sender_id],
    )

    dialog_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(
            'dialogs.id',
            ondelete='CASCADE',
        ),
        nullable=False,
    )
    dialog = relationship(
        'Dialog',
        backref=backref(
            name='messages',
            uselist=True,
        ),
        foreign_keys=[dialog_id],
    )

    text = sa.Column(
        sa.String(length=500),
        nullable=False,
    )
    is_read = sa.Column(
        sa.Boolean(),
        default=False,
    )

    def __str__(self) -> str:
        return f'Message {self.text}, dialog#{self.dialog_id}'
