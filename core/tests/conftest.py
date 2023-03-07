import asyncio
from typing import Generator

from fastapi.applications import FastAPI

import pytest
import pytest_asyncio
from faker.proxy import Faker

from core.apps.attachments.repositories.attachment_repository import AttachmentRepository
from core.apps.classroom.repositories import RoomRepository
from core.apps.classroom.repositories.assignment import HomeworkAssignmentRepository
from core.apps.classroom.repositories.participation_repository import ParticipationRepository
from core.apps.classroom.repositories.post_repository import RoomPostRepository
from core.apps.users.repositories.user_repository import UserRepository
from core.apps.users.services.user_service import UserService
from core.common.database import test_engine
from core.common.factory import AppFactory
from core.common.models.base import BaseDBModel
from core.tests.client import FastAPITestClient


@pytest.fixture(scope='module', autouse=True)
def app() -> FastAPI:
    yield AppFactory.create_app()


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
async def user_service() -> UserService:
    return UserService()


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
async def assignment_repository():
    return HomeworkAssignmentRepository()


@pytest_asyncio.fixture
async def attachment_repository():
    return AttachmentRepository()
