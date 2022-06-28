import sqlalchemy as sa

from apps.common.models.base import BaseDBModel


class Attachment(BaseDBModel):
    __tablename__ = 'attachments'

    source = sa.Column(sa.LargeBinary(), nullable=False)
    filename = sa.Column(sa.String(256), nullable=False)

    # post
    post_id: int = sa.Column(sa.Integer, sa.ForeignKey('posts.id'))
    assignment_id: int = sa.Column(sa.Integer, sa.ForeignKey('assignments.id'))

    def __str__(self) -> str:
        return f'Attachment: "{self.filename}"'

    def __repr__(self) -> str:
        return f'<{str(self)}>'

    class Meta:
        table = 'attachments'

    async def stream(self):
        yield self.source
