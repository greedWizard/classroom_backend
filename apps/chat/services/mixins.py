from tortoise.models import Model


class ChatPermissionsMixin:
    sender_field: str = 'recipient'
    reciever_field: str = 'sender'
    model: type[Model] = NotImplemented()
