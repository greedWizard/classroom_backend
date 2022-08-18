from datetime import datetime

import factory
from core.apps.users.models import User
from core.apps.users.repositories.user_repository import UserRepository
from core.apps.users.utils import hash_string
from core.tests.factories.base import AsyncRepositoryFactory


class UserFactory(AsyncRepositoryFactory):
    __repository__ = UserRepository()

    id = factory.Sequence(lambda n: n)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    middle_name = factory.Faker('first_name')
    password = factory.Sequence(lambda n: hash_string('123'))
    activation_token = factory.Faker('pystr')
    email = factory.Faker('email')
    phone_number = factory.Sequence(lambda n: f'+7{10000000000 + n}')
    created_at = datetime.utcnow()
    last_login = datetime.utcnow()
    is_active = True
    password_reset_deadline = None

    class Meta:
        model = User
