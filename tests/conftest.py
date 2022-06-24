import asyncio
import uuid
from datetime import datetime
from typing import Generator

import pytest
import pytest_asyncio
from faker.proxy import Faker
from starlette import status

from fastapi.applications import FastAPI
from fastapi.testclient import TestClient

from tortoise.contrib.test import (
    finalizer,
    initializer,
)

from apps.common.config import config
from apps.common.factory import AppFactory
from apps.user.models import User
from apps.user.utils import hash_string


@pytest.fixture(scope='module', autouse=True)
def app() -> FastAPI:
    yield AppFactory.create_app(test_mode=True)


@pytest.fixture(scope='session')
def fake() -> Generator:
    yield Faker()


@pytest.fixture(autouse=True, scope='module')
def client(app: FastAPI) -> Generator:
    initializer(config.APP_MODULES['models'])
    with TestClient(app) as c:
        yield c
    finalizer()


@pytest.fixture(scope='session')
def event_loop() -> Generator:
    loop = asyncio.get_event_loop()
    yield asyncio.get_event_loop()
    loop.close()


@pytest_asyncio.fixture
async def user(fake: Faker):
    password = '123'

    default_user_data = {
        'first_name': fake.name(),
        'last_name': fake.name(),
        'middle_name': fake.name(),
        'phone_number': '+70000000000',
        'password': hash_string(password),
        'activation_token': uuid.uuid4().hex,
        'email': fake.email(),
        'activation_deadline_dt': datetime.utcnow(),
        'is_active': True,
    }

    user, _ = await User.get_or_create(
        defaults=default_user_data,
    )
    return user


@pytest.fixture
def authentication_token(
    app: FastAPI,
    client: TestClient,
    user: User,
) -> str:
    url = app.url_path_for('authenticate_user')
    response = client.post(
        url,
        json={
            'email': user.email,
            'password': '123',
        },
    )
    assert response.status_code == status.HTTP_200_OK

    yield response.json()['access_token']
