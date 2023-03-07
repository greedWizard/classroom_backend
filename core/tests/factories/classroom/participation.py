from datetime import datetime

import factory

from core.apps.classroom.constants import ParticipationRoleEnum
from core.apps.classroom.models import Participation
from core.apps.classroom.repositories.participation_repository import ParticipationRepository
from core.tests.factories.base import AsyncRepositoryFactory
from core.tests.factories.classroom.room import RoomFactory
from core.tests.factories.user.user import UserFactory


class ParticipationFactory(AsyncRepositoryFactory):
    __repository__ = ParticipationRepository()

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
