from datetime import datetime

import factory

from core.apps.classroom.models import Room
from core.apps.classroom.repositories.room_repository import RoomRepository
from core.tests.factories.base import AsyncRepositoryFactory
from core.tests.factories.user.user import UserFactory


class RoomFactory(AsyncRepositoryFactory):
    __repository__ = RoomRepository()

    id = factory.Sequence(lambda n: n)
    created_at = datetime.utcnow()
    updated_at = datetime.utcnow()
    name = factory.Faker('job')
    description = factory.Faker('text')
    author = factory.SubFactory(UserFactory)
    updated_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Room
