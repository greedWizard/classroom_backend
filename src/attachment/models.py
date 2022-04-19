from tortoise import fields

from core.models import AuthorAbstract, TimeStampAbstract


class Attachment(AuthorAbstract, TimeStampAbstract):
    id = fields.IntField(pk=True)
    source = fields.BinaryField()
    filename = fields.CharField(100)
    type = fields.CharField(100, default='text')

    @property
    def download_link(self):
        return f'api/v1/attachments/{self.id}'

    def __str__(self) -> str:
        return f'Attachment: "{self.filename}" {self.download_link()}'

    def __repr__(self) -> str:
        return f'<{str(self)}>'
