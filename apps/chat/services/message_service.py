from apps.chat.models import Message
from common.services.base import CRUDService


class MessageService(CRUDService):
    model: type[Message] = Message
