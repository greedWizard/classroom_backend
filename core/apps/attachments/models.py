import sqlalchemy as sa

from core.common.models.base import BaseDBModel


class Attachment(BaseDBModel):
    __tablename__ = 'attachments'

    source = sa.Column(sa.LargeBinary(), nullable=False)
    filename = sa.Column(sa.String(256), nullable=False)
    is_profile_picture = sa.Column(sa.Boolean(), default=False)

    # post
    post_id: int = sa.Column(sa.Integer, sa.ForeignKey('posts.id', ondelete='CASCADE'))
    assignment_id: int = sa.Column(
        sa.Integer,
        sa.ForeignKey('assignments.id', ondelete='CASCADE'),
    )

    def __str__(self) -> str:
        return f'Attachment: "{self.filename}"'

    def __repr__(self) -> str:
        return f'<{str(self)}>'

    @property
    def is_attached_to_assignment(self):
        return bool(self.assignment_id)

    @property
    def is_attached_to_post(self):
        return bool(self.post_id)

    async def stream(self):
        yield self.source
