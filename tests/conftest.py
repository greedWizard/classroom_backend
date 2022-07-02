import asyncio
import uuid
from datetime import datetime
from typing import Generator

import pytest
import pytest_asyncio
from faker.proxy import Faker

from fastapi.applications import FastAPI

from apps.classroom.repositories import RoomRepository
from apps.classroom.repositories.participation_repository import ParticipationRepository
from apps.classroom.repositories.post_repository import RoomPostRepository
from apps.common.database import test_engine
from apps.common.factory import AppFactory
from apps.common.models.base import BaseDBModel
from apps.user.repositories.user_repository import UserRepository
from apps.user.utils import hash_string
from tests.client import FastAPITestClient


@pytest.fixture(scope='module', autouse=True)
def app() -> FastAPI:
    yield AppFactory.create_app(test_mode=True)


@pytest.fixture(scope='session')
def fake() -> Generator:
    yield Faker()


@pytest.fixture(scope='session')
def event_loop() -> Generator:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True, scope='function')
def client(app: FastAPI, event_loop: asyncio.AbstractEventLoop) -> Generator:
    connection = event_loop.run_until_complete(test_engine.connect())
    event_loop.run_until_complete(connection.run_sync(BaseDBModel.metadata.create_all))
    with FastAPITestClient(app) as c:
        yield c
    event_loop.run_until_complete(connection.run_sync(BaseDBModel.metadata.drop_all))


@pytest_asyncio.fixture
async def user_repository():
    return UserRepository()


@pytest_asyncio.fixture
async def room_repository():
    return RoomRepository()


@pytest_asyncio.fixture
async def participation_repository():
    return ParticipationRepository()


@pytest_asyncio.fixture
async def room_post_repository():
    return RoomPostRepository()


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
