from datetime import (
    datetime,
    timedelta,
)
from typing import Dict

import pytest
from faker import Faker

from fastapi import status
from fastapi.applications import FastAPI
from fastapi.testclient import TestClient

from apps.user.repositories.user_repository import UserRepository
from apps.user.utils import hash_string
from tests.factories.user import UserFactory


USER_TEST_PASSWORD = 'testpPassword123'
USER_TEST_UPDATE_PASSWORD = 'testpAssword321'


@pytest.fixture(scope='module')
def user_data(fake: Faker):
    yield {
        'first_name': fake.name(),
        'last_name': fake.name(),
        'email': fake.email(),
        'password': hash_string(USER_TEST_PASSWORD),
        'phone_number': '+79990001122',
        'activation_token': 'test_activation_token',
        'activation_deadline_dt': datetime.utcnow(),
    }


@pytest.mark.asyncio
async def test_authentication_fail_not_active(
    app: FastAPI,
    client: TestClient,
    user_repository: UserRepository,
):
    user = await UserFactory.create(password=hash_string(USER_TEST_PASSWORD))

    url = app.url_path_for('authenticate_user')
    await user_repository.update(
        values={
            'is_active': False,
            'password': hash_string(USER_TEST_PASSWORD),
        },
    )

    response = client.post(
        url,
        json={
            'email': user.email,
            'password': USER_TEST_PASSWORD,
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_user_activation(
    app: FastAPI,
    client: TestClient,
    user_repository: UserRepository,
):
    user = await UserFactory.create(is_active=False)

    assert not await user_repository.fetch(is_active=True)

    url = app.url_path_for('activate_user', activation_token=user.activation_token)
    client.get(url)

    user = await user_repository.refresh(user)
    assert user.is_active


@pytest.mark.asyncio
async def test_authentication_success_email(
    app: FastAPI,
    client: TestClient,
    user_repository: UserRepository,
):
    url = app.url_path_for('authenticate_user')
    user = await UserFactory.create(
        password=hash_string(USER_TEST_PASSWORD),
        is_active=True,
        last_login=datetime.utcnow() - timedelta(days=7),
    )

    response = client.post(
        url,
        json={
            'email': user.email,
            'password': USER_TEST_PASSWORD,
        },
    )
    json_data = response.json()
    user = await user_repository.refresh(user)

    assert response.status_code == status.HTTP_200_OK, json_data
    assert 'access_token' in json_data
    assert 'refresh_token' in json_data
    assert user.last_login.date() == datetime.utcnow().date()


@pytest.mark.asyncio
async def test_authentication_success_phone(
    app: FastAPI,
    client: TestClient,
):
    url = app.url_path_for('authenticate_user')
    user = await UserFactory.create(
        is_active=True,
        password=hash_string(USER_TEST_PASSWORD),
    )

    response = client.post(
        url,
        json={
            'phone_number': user.phone_number,
            'password': USER_TEST_PASSWORD,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()

    assert 'access_token' in json_data
    assert 'refresh_token' in json_data

    access_token = json_data['access_token']

    url = app.url_path_for('current_user_info')
    response = client.get(
        url,
        headers={
            'Authorization': f'Bearer {access_token}',
        },
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_authentication_fail_phone(
    app: FastAPI,
    client: TestClient,
):
    await UserFactory.create()
    url = app.url_path_for('authenticate_user')

    response = client.post(
        url,
        json={
            'phone_number': '+0000000000',
            'password': USER_TEST_PASSWORD,
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_authentication_fail_email(
    app: FastAPI,
    client: TestClient,
):
    url = app.url_path_for('authenticate_user')
    await UserFactory.create()

    response = client.post(
        url,
        json={
            'email': 'notauseremail@notamail.com',
            'password': USER_TEST_PASSWORD,
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_any_user_info(
    app: FastAPI,
    client: TestClient,
    user_data: Dict,
):
    url = app.url_path_for('authenticate_user')
    user = await UserFactory.create(password=hash_string(USER_TEST_PASSWORD))

    response = client.post(
        url,
        json={
            'email': user.email,
            'password': USER_TEST_PASSWORD,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()

    assert 'access_token' in json_data
    assert 'refresh_token' in json_data

    access_token = json_data['access_token']

    url = app.url_path_for('user_info', user_id=user.id)

    response = client.get(
        url,
        headers={
            'Authorization': f'Bearer {access_token}',
        },
    )

    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()

    for key in list(json_data.keys()):
        if key in user_data:
            assert getattr(user, key) == json_data[key], key


@pytest.mark.asyncio
async def test_current_user_update(
    app: FastAPI,
    client: TestClient,
    fake: Faker,
):
    url = app.url_path_for('authenticate_user')
    user = await UserFactory.create(password=hash_string(USER_TEST_PASSWORD))

    new_user_data = {
        'email': fake.email(),
        'first_name': fake.name(),
        'last_name': fake.name(),
        'password': USER_TEST_UPDATE_PASSWORD,
        'repeat_password': USER_TEST_UPDATE_PASSWORD,
        'confirm_password': USER_TEST_PASSWORD,
    }

    response = client.post(
        url,
        json={
            'email': user.email,
            'password': USER_TEST_PASSWORD,
        },
    )
    json_data = response.json()

    assert response.status_code == status.HTTP_200_OK, json_data

    assert 'access_token' in json_data
    assert 'refresh_token' in json_data

    access_token = json_data['access_token']

    url = app.url_path_for('update_current_user')

    response = client.put(
        url,
        json=new_user_data,
        headers={'Authorization': f'Bearer {access_token}'},
    )

    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()

    for key in list(json_data.keys()):
        if key in new_user_data:
            assert new_user_data[key] == json_data[key]


@pytest.mark.asyncio
async def test_current_user_update_incorrect_password(
    app: FastAPI,
    client: TestClient,
    fake: Faker,
):
    url = app.url_path_for('authenticate_user')
    user = await UserFactory.create(password=hash_string(USER_TEST_PASSWORD))

    new_user_data = {
        'email': fake.email(),
        'first_name': fake.name(),
        'last_name': fake.name(),
        'password': USER_TEST_UPDATE_PASSWORD,
        'repeat_password': USER_TEST_UPDATE_PASSWORD,
        'confirm_password': '12345',
    }

    response = client.post(
        url,
        json={
            'email': user.email,
            'password': USER_TEST_PASSWORD,
        },
    )
    json_data = response.json()

    assert response.status_code == status.HTTP_200_OK, json_data

    assert 'access_token' in json_data
    assert 'refresh_token' in json_data

    access_token = json_data['access_token']

    url = app.url_path_for('update_current_user')

    response = client.put(
        url,
        json=new_user_data,
        headers={'Authorization': f'Bearer {access_token}'},
    )
    json_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST, json_data

    for key in list(json_data.keys()):
        if key in new_user_data:
            assert new_user_data[key] != json_data[key]
