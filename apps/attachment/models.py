import sqlalchemy as sa

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

    def __str__(self) -> str:
        return f'Attachment: "{self.filename}"'

    def __repr__(self) -> str:
        return f'<{str(self)}>'

    async def stream(self):
        yield self.source
