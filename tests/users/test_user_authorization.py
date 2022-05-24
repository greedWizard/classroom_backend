from datetime import datetime
from typing import Dict

import pytest
from faker import Faker

from fastapi import status
from fastapi.applications import FastAPI
from fastapi.testclient import TestClient

from apps.user.models import User
from apps.user.utils import hash_string


USER_TEST_PASSWORD = 'testpPassword123'
USER_TEST_UPDATE_PASSWORD = 'testpAssword321'


@pytest.fixture(scope='module')
def user_data(
    fake: Faker,
):
    yield {
        'id': 1,
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
    user: User,
    app: FastAPI,
    client: TestClient,
    user_data: dict,
):
    await User.update_or_create(
        defaults=user_data,
    )
    await user.refresh_from_db()

    url = app.url_path_for('authenticate_user')
    await User.all().update(is_active=False, password=hash_string(USER_TEST_PASSWORD))

    response = client.post(
        url,
        json={
            'email': user.email,
            'password': USER_TEST_PASSWORD,
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert (
        response.json()['detail'] == 'User is not active. Please activate your profile.'
    )


@pytest.mark.asyncio
async def test_user_activation(
    user: User,
    app: FastAPI,
    client: TestClient,
):
    await User.all().update(is_active=False)
    await user.refresh_from_db()
    assert not user.is_active

    url = app.url_path_for('activate_user', activation_token=user.activation_token)

    client.get(url)

    await user.refresh_from_db()
    assert user.is_active


@pytest.mark.asyncio
async def test_authentication_success_email(
    user: User,
    app: FastAPI,
    client: TestClient,
    user_data: Dict,
):
    url = app.url_path_for('authenticate_user')

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

    url = app.url_path_for('current_user_info')

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
            assert user_data[key] == json_data[key], key


@pytest.mark.asyncio
async def test_authentication_success_phone(
    user: User,
    app: FastAPI,
    client: TestClient,
    user_data: Dict,
):
    url = app.url_path_for('authenticate_user')

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
    json_data = response.json()

    for key in list(json_data.keys()):
        if key in user_data:
            assert user_data[key] == json_data[key], key


@pytest.mark.asyncio
async def test_authentication_fail_phone(
    app: FastAPI,
    client: TestClient,
):
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
    user: User,
    app: FastAPI,
    client: TestClient,
    user_data: Dict,
):
    url = app.url_path_for('authenticate_user')

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
            assert user_data[key] == json_data[key], key


@pytest.mark.asyncio
async def test_current_user_update(
    user: User,
    app: FastAPI,
    client: TestClient,
    fake: Faker,
):
    url = app.url_path_for('authenticate_user')

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

    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()

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
