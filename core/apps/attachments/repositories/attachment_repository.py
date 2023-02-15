from core.apps.attachments.models import Attachment
from core.common.repositories.base import CRUDRepository


class AttachmentRepository(CRUDRepository):
    _model: type[Attachment] = Attachment

    async def create_picture(
        self,
        filename: str,
        source: bytes,
        **kwargs,
    ) -> Attachment:
        created_object = await self.create(
            filename=filename,
            source=source,
            is_profile_picture=True,
            **kwargs,
        )

        return created_object
