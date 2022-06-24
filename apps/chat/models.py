from tortoise import fields

from apps.common.models import TimeStampAbstract


class Dialog(TimeStampAbstract):
    id = fields.IntField(pk=True)
    reciever = fields.ForeignKeyField(
        'models.User',
        related_name='recieved_dialogues',
        on_delete=fields.SET_NULL,
        null=True,
        blank=True,
    )
    sender = fields.ForeignKeyField(
        'models.User',
        related_name='sent_dialogues',
        on_delete=fields.SET_NULL,
        null=True,
    )

    class Meta:
        unique_together = ('reciever_id', 'sender_id')
        table = 'dialogues'

    def __str__(self) -> str:
        return (
            f'Dialog #{self.id} from user #{self.sender_id} to user #{self.reciever_id}'
        )

    def __repr__(self) -> str:
        return f'<{self}>'


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
        related_name='messages',
        on_delete=fields.CASCADE,
    )
    text = fields.TextField()

    class Meta:
        table = 'messages'

    def __str__(self) -> str:
        return f'Message {self.text}'

    def __repr__(self) -> str:
        return f'<{self}>'
