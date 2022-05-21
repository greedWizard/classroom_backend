import string

from factory_boy_extra.tortoise_factory import TortoiseModelFactory
from faker.proxy import Faker

import factory
from apps.user.models import User
from factory import fuzzy


fake = Faker()


class UserFactory(TortoiseModelFactory):
    first_name = fake.first_name()
    last_name = fake.last_name()
    middle_name = fake.pystr()
    password = fake.pystr()
    rating = fake.pyint()
    last_login = None
    activation_token = fake.md5()
    activation_deadline_dt = fake.future_datetime()
    is_active = True
    is_reset_needed = False
    phone_number = fuzzy.FuzzyText('+7', length=10, chars=string.digits)
    email = factory.Faker('email')
    gender = 'male'

    class Meta:
        model = User
