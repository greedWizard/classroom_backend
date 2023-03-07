from datetime import datetime

import factory

from core.apps.chat.models import Message
from core.apps.chat.repositories.message_repository import MessageRepository
from core.tests.factories.base import AsyncRepositoryFactory
from core.tests.factories.chat.dialog import DialogFactory
from core.tests.factories.user.user import UserFactory


class MessageFactory(AsyncRepositoryFactory):
    __repository__: MessageRepository = MessageRepository()

    created_at = datetime.utcnow()
    updated_at = datetime.utcnow()
    text = factory.Faker('text')
    is_read = False
    dialog = factory.SubFactory(DialogFactory)
    sender = factory.SubFactory(UserFactory)

    class Meta:
        model = Message
