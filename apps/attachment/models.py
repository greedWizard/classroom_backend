import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref

from apps.common.models.base import BaseDBModel


class Attachment(BaseDBModel):
    __tablename__ = 'attachments'

    source = sa.Column(sa.LargeBinary(), nullable=False)
    filename = sa.Column(sa.String(256), nullable=False)

    # post
    post_id: int = sa.Column(sa.Integer, sa.ForeignKey('posts.id', ondelete='CASCADE'))
    assignment_id: int = sa.Column(
        sa.Integer, sa.ForeignKey('assignments.id', ondelete='CASCADE')
    )
    profile_picture_user_id = sa.Column(
        sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'),
    )
    user = relationship(
        'User',
        backref=backref('attachments', uselist=False),
        foreign_keys=[profile_picture_user_id],
    )

    def __str__(self) -> str:
        return f'Attachment: "{self.filename}" {self.profile_picture_user_id}'

    def __repr__(self) -> str:
        return f'<{str(self)}>'

    async def stream(self):
        yield self.source
