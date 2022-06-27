from datetime import datetime

import factory

from apps.user.models import User
from apps.user.repositories.user_repository import UserRepository
from apps.user.utils import hash_string

from .base import AsyncRepositoryFactory


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

    class Meta:
        model = User
