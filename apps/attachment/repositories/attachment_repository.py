from apps.attachment.models import Attachment
from apps.common.repositories.base import CRUDRepository


class AttachmentRepository(CRUDRepository):
    _model: type[Attachment] = Attachment
