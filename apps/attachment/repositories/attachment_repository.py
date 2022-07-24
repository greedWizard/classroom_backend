from apps.attachment.models import Attachment
from apps.common.repositories.base import CRUDRepository


class AttachmentRepository(CRUDRepository):
    _model: type[Attachment] = Attachment

    async def create_picture(self, filename: str, source: bytes, **args) -> Attachment:
        created_object = await self.create(
            filename=filename,
            source=source,
            **args,
        )

        return created_object
