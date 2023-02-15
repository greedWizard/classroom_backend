from datetime import datetime

import factory

from core.apps.chat.models import Dialog
from core.apps.chat.repositories.dialog_repository import DialogRepository
from core.tests.factories.base import AsyncRepositoryFactory
from core.tests.factories.user.user import UserFactory


class DialogFactory(AsyncRepositoryFactory):
    __repository__: DialogRepository = DialogRepository()

    id = factory.Sequence(lambda n: n)
    created_at = datetime.utcnow()
    updated_at = datetime.utcnow()
    author = factory.SubFactory(UserFactory)
    updated_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Dialog
