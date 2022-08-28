from datetime import datetime

import factory

from core.apps.chat.models import Message
from core.apps.chat.repositories.dialog_repository import DialogRepository
from core.tests.factories.base import AsyncRepositoryFactory
from core.tests.factories.chat.dialog import DialogFactory
from core.tests.factories.user.user import UserFactory


class MessageFactory(AsyncRepositoryFactory):
    __repository__: DialogRepository = DialogRepository()

    id = factory.Sequence(lambda n: n)
    created_at = datetime.utcnow()
    updated_at = datetime.utcnow()
    text = factory.Faker('text')
    is_read = False
    dialog = factory.SubFactory(DialogFactory)
    sender = factory.SubFactory(UserFactory)

    class Meta:
        model = Message
