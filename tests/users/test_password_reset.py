from unittest import mock

import pytest

from fastapi import status
from fastapi.applications import FastAPI
from fastapi.testclient import TestClient

from apps.user.models import User
from apps.user.repositories.user_repository import UserRepository
from tests.factories.user import UserFactory


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
    url = app.url_path_for('initiate_user_password_reset')

    with mock.patch('scheduler.tasks.user.send_password_reset_email'):
        response = client.post(
            url,
            json={
                'email': user.email,
            },
        )

    user: User = await user_repository.refresh(user)

    assert response.status_code == status.HTTP_200_OK, response.json()
    assert user.is_reset_needed
    assert user.password_reset_deadline
