from datetime import datetime

import factory

from core.apps.classroom.models.topics import Topic
from core.apps.classroom.repositories.topic_repository import TopicRepository
from core.tests.factories.base import AsyncRepositoryFactory
from core.tests.factories.classroom.room import RoomFactory
from core.tests.factories.user.user import UserFactory


class TopicFactory(AsyncRepositoryFactory):
    __repository__ = TopicRepository()

    # TODO: AbstractBaseFactoryMixin
    created_at = datetime.utcnow()
    updated_at = datetime.utcnow()
    room = factory.SubFactory(RoomFactory)
    author = factory.SubFactory(UserFactory)
    updated_by = factory.SubFactory(UserFactory)
    title = factory.Faker('name')
    order = factory.Faker('pyint')

    class Meta:
        model = Topic
