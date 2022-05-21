from tortoise import fields

from common.models import AuthorAbstract, TimeStampAbstract


class Dialog(TimeStampAbstract, AuthorAbstract):
    id = fields.IntField(pk=True)
    subject_post = fields.ForeignKeyField(
        'models.RoomPost',
        related_name='recieved_messages',
        on_delete=fields.CASCADE,
    )


class Message(TimeStampAbstract):
    id = fields.IntField(pk=True)
    reciever = fields.ForeignKeyField(
        'models.User',
        related_name='recieved_messages',
        on_delete=fields.SET_NULL,
        null=True,
        blank=True,
    )
    sender = fields.ForeignKeyField(
        'models.User',
        related_name='sent_messages',
        on_delete=fields.SET_NULL,
        null=True,
    )
    dialog = fields.ForeignKeyField(
        'models.Dialog',
        related_name='sent_messages',
        on_delete=fields.CASCADE,
    )
    text = fields.TextField()
