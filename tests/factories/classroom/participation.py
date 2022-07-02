from datetime import datetime

import factory

from apps.classroom.constants import ParticipationRoleEnum
from apps.classroom.models import Participation
from apps.classroom.repositories.participation_repository import ParticipationRepository
from tests.factories.base import AsyncRepositoryFactory
from tests.factories.classroom.room import RoomFactory
from tests.factories.user.user import UserFactory


class ParticipationFactory(AsyncRepositoryFactory):
    __repository__ = ParticipationRepository()

    id = factory.Sequence(lambda n: n)
    created_at = datetime.utcnow()
    updated_at = datetime.utcnow()
    user = factory.SubFactory(UserFactory)
    room = factory.SubFactory(RoomFactory)
    role = factory.Faker(
        'random_element',
        elements=[role.value for role in ParticipationRoleEnum],
    )
    author = factory.SubFactory(UserFactory)
    updated_by = factory.SubFactory(UserFactory)

    class Meta:
        model = Participation
