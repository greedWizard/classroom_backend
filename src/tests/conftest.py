import asyncio
from datetime import datetime
import hashlib
import pytest
from typing import Generator
import uuid

from faker.proxy import Faker

from starlette import status
from fastapi.applications import FastAPI
from fastapi.testclient import TestClient

from tortoise.contrib.test import finalizer, initializer

from user.models import User
from core.config import config
from core.factory import AppFactory
from tests.utils.app import app


@pytest.fixture(scope='module', autouse=True)
def app() -> FastAPI:
    yield AppFactory.create_app(test_mode=True)


@pytest.fixture(scope='session')
def fake() -> Generator:
    yield Faker()


@pytest.fixture(autouse=True, scope='module')
def client(
    app: FastAPI,
) -> Generator:
    initializer(config.APP_MODULES['models'])
    with TestClient(app) as c:
        yield c
    finalizer()


@pytest.fixture
def event_loop() -> Generator:
    yield asyncio.get_event_loop()



@pytest.fixture
def authentication_token(
    event_loop: asyncio.AbstractEventLoop,
    fake: Faker,
    app: FastAPI,
    client: TestClient
) -> str:
    password = '123'
    default_user_data = {
        'first_name': fake.name(),
        'last_name': fake.name(),
        'middle_name': fake.name(),
        'phone_number': f'+70000000000',
        'password': hashlib.md5(password.encode()).hexdigest(),
        'activation_token': uuid.uuid4().hex,
        'email': fake.email(),
        'activation_deadline_dt': datetime.utcnow(),
        'is_active': True,
    }

    user, _ = event_loop.run_until_complete(
        User.get_or_create(
            defaults=default_user_data,
        )
    )
    
    url = app.url_path_for('authenticate_user')
    response = client.post(url, json={
        'email': user.email,
        'password': '123',
    })
    assert response.status_code == status.HTTP_200_OK

    yield response.json()['access_token']
