from datetime import datetime

import factory

from apps.classroom.constants import HomeWorkAssignmentStatus, ParticipationRoleEnum
from apps.classroom.models import HomeworkAssignment, Participation
from apps.classroom.repositories.assignment import HomeworkAssignmentRepository
from apps.classroom.repositories.participation_repository import ParticipationRepository
from tests.factories.base import AsyncRepositoryFactory
from tests.factories.classroom.room import RoomFactory
from tests.factories.classroom.room_post import RoomPostFactory
from tests.factories.user.user import UserFactory


class AssignmentFactory(AsyncRepositoryFactory):
    __repository__ = HomeworkAssignmentRepository()

    id = factory.Sequence(lambda n: n)
    created_at = datetime.utcnow()
    updated_at = datetime.utcnow()
    author = factory.SubFactory(UserFactory)
    updated_by = factory.SubFactory(UserFactory)

    status = factory.Faker(
        'random_element',
        elements=[status.value for status in HomeWorkAssignmentStatus],
    )
    rate = factory.Faker('random_element', elements=range(0, 6))
    comment = factory.Faker('text')
    post = factory.SubFactory(RoomPostFactory)

    class Meta:
        model = HomeworkAssignment
