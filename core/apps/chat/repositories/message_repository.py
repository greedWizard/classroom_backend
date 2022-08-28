from core.apps.chat.models import Message
from core.common.repositories.base import CRUDRepository


class MessageRepository(CRUDRepository):
    _model = Message
