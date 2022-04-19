from attachment.models import Attachment
from core.services.base import CRUDService


class AttachmentService(CRUDService):
    model = Attachment
