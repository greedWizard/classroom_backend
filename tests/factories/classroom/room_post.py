from datetime import datetime

import factory

from apps.classroom.constants import RoomPostType
from apps.classroom.models import RoomPost
from apps.classroom.repositories.post_repository import RoomPostRepository
from tests.factories.base import AsyncRepositoryFactory
from tests.factories.classroom.room import RoomFactory
from tests.factories.user.user import UserFactory


class RoomPostFactory(AsyncRepositoryFactory):
    __repository__ = RoomPostRepository()

    # TODO: AbstractBaseFactoryMixin
    id = factory.Sequence(lambda n: n)
    created_at = datetime.utcnow()
    updated_at = datetime.utcnow()
    room = factory.SubFactory(RoomFactory)
    author = factory.SubFactory(UserFactory)
    updated_by = factory.SubFactory(UserFactory)
    title = factory.Faker('name')
    description = factory.Faker('text')
    text = factory.Faker('text')
    deadline_at = factory.Faker('future_date')
    type = factory.Faker(
        'random_element',
        elements=[role.value for role in RoomPostType],
    )

    class Meta:
        model = RoomPost
