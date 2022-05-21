from tortoise import fields

from common.models import (
    AuthorAbstract,
    TimeStampAbstract,
)


class Attachment(AuthorAbstract, TimeStampAbstract):
    id = fields.IntField(pk=True)
    source = fields.BinaryField()
    filename = fields.CharField(max_length=256)

    @property
    def download_link(self):
        return f'api/v1/attachments/{self.id}'

    def __str__(self) -> str:
        return f'Attachment: "{self.filename}" {self.download_link}'

    def __repr__(self) -> str:
        return f'<{str(self)}>'

    class Meta:
        table = 'attachments'

    async def stream(self):
        yield self.source
