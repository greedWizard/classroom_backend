from datetime import timedelta
from unittest import mock

from fastapi import status
from fastapi.applications import FastAPI
from fastapi.testclient import TestClient

import pytest
from itsdangerous import TimedSerializer

from core.apps.users.models import User
from core.apps.users.repositories.user_repository import UserRepository
from core.common.config import config
from core.common.utils import (
    get_current_datetime,
    sign_timed_token,
)
from core.tests.factories.user import UserFactory


@pytest.mark.asyncio
async def test_initiate_password_reset_fails_invalid_email(
    app: FastAPI,
    client: TestClient,
):
    invalid_email = 'invalidemail@mail.ru'
    await UserFactory.create()

    url = app.url_path_for('initiate_user_password_reset')

    response = client.post(
        url,
        json={
            'email': invalid_email,
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()


@pytest.mark.asyncio
async def test_initiate_password_reset_success(
    app: FastAPI,
    client: TestClient,
    user_repository: UserRepository,
):
    user = await UserFactory.create()
    assert not user.is_reset_needed

    url = app.url_path_for('initiate_user_password_reset')

    with mock.patch('core.scheduler.tasks.user.send_password_reset_email'):
        response = client.post(
            url,
            json={
                'email': user.email,
            },
        )

    user: User = await user_repository.refresh(user)

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert not user.is_reset_needed
    assert user.password_reset_deadline


@pytest.mark.asyncio
async def test_user_reset_password_no_cookie_provided(
    app: FastAPI,
    client: TestClient,
    user_repository: UserRepository,
):
    user = await UserFactory.create()
    previous_password = user.password

    url = app.url_path_for('reset_user_password', token=user.activation_token)
    response = client.post(
        url=url,
        json={
            'password': 'new_password',
            'repeat_password': 'new_password',
        },
    )
    user = await user_repository.refresh(user)

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert user.password == previous_password


@pytest.mark.asyncio
async def test_user_reset_password_wrong_cookie_provided(
    app: FastAPI,
    client: TestClient,
    user_repository: UserRepository,
):
    user = await UserFactory.create(
        is_reset_needed=True,
        password_reset_deadline=get_current_datetime() + timedelta(minutes=30),
    )
    previous_password = user.password

    url = app.url_path_for('reset_user_password', token=user.activation_token)
    response = client.post(
        url=url,
        json={
            'password': 'new_password',
            'repeat_password': 'new_password',
        },
        cookies={
            'token': 'defenately wrong token',
        },
    )
    user = await user_repository.refresh(user)

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert user.password == previous_password


@pytest.mark.asyncio
async def test_user_reset_password_too_late(
    app: FastAPI,
    client: TestClient,
    user_repository: UserRepository,
):
    user = await UserFactory.create(
        is_reset_needed=True,
        password_reset_deadline=get_current_datetime() - timedelta(minutes=30),
    )
    previous_password = user.password
    token = TimedSerializer(secret_key=config.APP_SECRET_KEY).dumps(
        user.id,
        salt=config.PASSWORD_RESET_SALT,
    )

    url = app.url_path_for('reset_user_password', token=user.activation_token)
    response = client.post(
        url=url,
        json={
            'password': 'new_password',
            'repeat_password': 'new_password',
        },
        cookies={'token': token},
    )
    user = await user_repository.refresh(user)

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert user.password == previous_password


@pytest.mark.asyncio
async def test_user_reset_password_success(
    app: FastAPI,
    client: TestClient,
    user_repository: UserRepository,
):
    user = await UserFactory.create(
        is_reset_needed=True,
        password_reset_deadline=get_current_datetime() + timedelta(minutes=30),
    )
    previous_password = user.password
    token = await sign_timed_token(user.id)

    url = app.url_path_for('reset_user_password', token=token)
    response = client.post(
        url=url,
        json={
            'password': 'new_passwOrd123',
            'repeat_password': 'new_passwOrd123',
        },
    )
    user = await user_repository.refresh(user)

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert user.password != previous_password


@pytest.mark.asyncio
async def test_user_reset_password_not_in_need(
    app: FastAPI,
    client: TestClient,
    user_repository: UserRepository,
):
    user = await UserFactory.create(
        is_reset_needed=False,
        password_reset_deadline=get_current_datetime() + timedelta(minutes=30),
    )
    previous_password = user.password
    token = TimedSerializer(secret_key=config.APP_SECRET_KEY).dumps(
        user.id,
        salt=config.PASSWORD_RESET_SALT,
    )

    url = app.url_path_for('reset_user_password', token=user.activation_token)
    response = client.post(
        url=url,
        json={
            'password': 'new_passwOrd123',
            'repeat_password': 'new_passwOrd123',
        },
        cookies={'token': token},
    )
    user = await user_repository.refresh(user)

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert user.password == previous_password, user


@pytest.mark.asyncio
async def test_user_reset_passwords_dont_match(
    app: FastAPI,
    client: TestClient,
    user_repository: UserRepository,
):
    user = await UserFactory.create(
        is_reset_needed=True,
        password_reset_deadline=get_current_datetime() + timedelta(minutes=30),
    )
    previous_password = user.password
    token = TimedSerializer(secret_key=config.APP_SECRET_KEY).dumps(
        user.id,
        salt=config.PASSWORD_RESET_SALT,
    )

    url = app.url_path_for('reset_user_password', token=user.activation_token)
    response = client.post(
        url=url,
        json={
            'password': 'new_passwOrd1234',
            'repeat_password': 'new_passwOrd123',
        },
        cookies={'token': token},
    )
    user = await user_repository.refresh(user)

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert user.password == previous_password


@pytest.mark.asyncio
async def test_user_reset_password_too_short(
    app: FastAPI,
    client: TestClient,
    user_repository: UserRepository,
):
    user = await UserFactory.create(
        is_reset_needed=True,
        password_reset_deadline=get_current_datetime() + timedelta(minutes=30),
    )
    previous_password = user.password
    token = TimedSerializer(secret_key=config.APP_SECRET_KEY).dumps(
        user.id,
        salt=config.PASSWORD_RESET_SALT,
    )

    url = app.url_path_for('reset_user_password', token=user.activation_token)
    response = client.post(
        url=url,
        json={
            'password': 'nE34',
            'repeat_password': 'nE34',
        },
        cookies={'token': token},
    )
    user = await user_repository.refresh(user)

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert user.password == previous_password
