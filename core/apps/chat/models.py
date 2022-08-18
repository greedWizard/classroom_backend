import sqlalchemy as sa
from sqlalchemy.orm import (
    backref,
    relationship,
)

from core.common.models.base import BaseDBModel
from core.common.models.mixins import AuthorAbstract


dialogs_participants = sa.Table(
    'dialogs_participants',
    BaseDBModel.metadata,
    sa.Column(
        'user_id',
        sa.Integer(),
        sa.ForeignKey(
            'users.id',
            ondelete='CASCADE',
        ),
        nullable=True,
        primary_key=True,
    ),
    sa.Column(
        'dialog_id',
        sa.Integer(),
        sa.ForeignKey(
            'dialogs.id',
            ondelete='CASCADE',
        ),
        nullable=True,
        primary_key=True,
    ),
)


class Dialog(BaseDBModel, AuthorAbstract):
    __tablename__ = 'dialogs'

    participants = relationship(
        'User',
        secondary=dialogs_participants,
        backref=backref(
            'dialogs',
            uselist=True,
        ),
    )

    def __str__(self) -> str:
        return (
            f'Dialog #{self.id} from user #{self.sender_id} to user #{self.reciever_id}'
        )

    def __repr__(self) -> str:
        return f'<{self}>'


class Message(BaseDBModel):
    __tablename__ = 'messages'

    reciever_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(
            'users.id',
            ondelete='CASCADE',
        ),
        nullable=False,
    )
    reciever = relationship(
        'User',
        backref=backref(
            name='received_messages',
            uselist=True,
        ),
        foreign_keys=[reciever_id],
    )

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
        sa.Text(length=300),
        nullable=False,
    )

    def __str__(self) -> str:
        return f'Message {self.text}, dialog#{self.dialog_id}'
