from tortoise import fields, models

from core.models import AuthorAbstract, TimeStampAbstract


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
        blank=True,
    )
    text = fields.TextField()