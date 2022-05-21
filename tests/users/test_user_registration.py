import pytest
from faker import Faker
from pytest_mock import MockerFixture

from fastapi import status
from fastapi.applications import FastAPI
from fastapi.testclient import TestClient

from apps.user.models import User
from apps.user.utils import hash_string


@pytest.fixture(scope='session')
def phone_number(fake: Faker) -> str:
    yield f'+{fake.random_int(1 * 10*11, int("9" * 13))}'


@pytest.fixture(scope='session')
def email(fake: Faker) -> str:
    yield fake.email()


@pytest.mark.asyncio
async def test_user_registration_success(
    app: FastAPI,
    client: TestClient,
    phone_number: str,
    email: str,
    mocker: MockerFixture,
):
    url = app.router.url_path_for('register_user')
    password = 'KjoiunslAdjkl19'

    user_count = await User.all().count()

    assert not user_count

    user_creds = {
        'first_name': 'Валерий',
        'last_name': 'Жмышенко',
        'middle_name': 'Альбретович',
        'phone_number': phone_number,
        'password': password,
        'repeat_password': password,
        'accept_eula': True,
        'email': email,
    }

    mocker.patch('common.services.email.EmailService.send_email')

    response = client.post(url, json=user_creds)

    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert await User.all().count() == user_count + 1

    user = await User.all().first()

    assert user.first_name == user_creds['first_name']
    assert user.last_name == user_creds['last_name']
    assert user.middle_name == user_creds['middle_name']
    assert user.password == hash_string(password)
    assert user.activation_token
    assert user.created_at.date()


@pytest.mark.asyncio
async def test_user_registration_phone_and_email_taken(
    app: FastAPI,
    client: TestClient,
    fake: Faker,
):
    url = app.router.url_path_for('register_user')
    password = 'Kjoisun41241kl19'

    user_count = await User.all().count()
    user = await User.all().first()

    assert user_count

    user_creds = {
        'first_name': fake.name(),
        'last_name': fake.name(),
        'middle_name': fake.name(),
        'phone_number': user.phone_number,
        'password': password,
        'repeat_password': password,
        'accept_eula': True,
        'email': user.email,
    }

    response = client.post(url, json=user_creds)
    json_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        json_data['detail']['phone_number']
        == 'User with that phone number is already registred.'
    )
    assert json_data['detail']['email'] == 'User with that email is already registred.'
    assert await User.all().count() == user_count


@pytest.mark.asyncio
async def test_user_registration_eula_is_not_accepted(
    app: FastAPI,
    client: TestClient,
    fake: Faker,
):
    url = app.router.url_path_for('register_user')
    password = 'Kjoisun41241kl19'

    user_count = User.all().count()

    assert user_count

    user_creds = {
        'first_name': fake.name(),
        'last_name': fake.name(),
        'middle_name': fake.name(),
        'phone_number': '+79997078922',
        'email': 'jma@mail.ru',
        'password': password,
        'repeat_password': password,
        'accept_eula': False,
    }

    response = client.post(url, json=user_creds)
    json_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json_data['detail']['accept_eula'] == 'Please accept eula and try again.'


@pytest.mark.asyncio
async def test_user_registration_eula_is_not_assigned(
    app: FastAPI,
    client: TestClient,
    fake: Faker,
):
    url = app.router.url_path_for('register_user')
    password = 'Kjoisun41241kl19'

    user_count = await User.all().count()

    assert user_count

    user_creds = {
        'first_name': fake.name(),
        'last_name': fake.name(),
        'middle_name': fake.name(),
        'phone_number': '+79997078922',
        'email': 'jma@mail.ru',
        'password': password,
        'repeat_password': password,
    }

    response = client.post(url, json=user_creds)
    json_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json_data['detail']['accept_eula'] == 'Please accept eula and try again.'


@pytest.mark.asyncio
async def test_user_registration_passwords_dont_match(
    app: FastAPI,
    client: TestClient,
    fake: Faker,
):
    url = app.router.url_path_for('register_user')
    password = 'Kjoisun41241kl19'

    user_count = await User.all().count()

    assert user_count

    user_creds = {
        'first_name': fake.name(),
        'last_name': fake.name(),
        'middle_name': fake.name(),
        'phone_number': '+79997078922',
        'password': password + '123',
        'email': 'jma@mail.ru',
        'repeat_password': password,
        'accept_eula': True,
    }

    response = client.post(url, json=user_creds)
    json_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json_data['detail']['password'] == "Passwords don't match."


@pytest.mark.asyncio
async def test_user_registration_multiple_errors(
    app: FastAPI,
    client: TestClient,
    fake: Faker,
):
    url = app.router.url_path_for('register_user')
    password = 'Kjoisun41241kl19'

    user_count = await User.all().count()
    user = await User.all().first()

    assert user_count

    user_creds = {
        'first_name': fake.name(),
        'last_name': fake.name(),
        'middle_name': fake.name(),
        'phone_number': user.phone_number,
        'email': 'jma@mail.ru',
        'password': password + '123',
        'repeat_password': password,
        'accept_eula': False,
    }

    response = client.post(url, json=user_creds)
    json_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json_data['detail']['password'] == "Passwords don't match."
    assert (
        json_data['detail']['phone_number']
        == 'User with that phone number is already registred.'
    )
    assert json_data['detail']['accept_eula'] == 'Please accept eula and try again.'
