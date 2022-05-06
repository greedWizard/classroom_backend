import asyncio
from faker.proxy import Faker
from fastapi.applications import FastAPI
import pytest
from typing import Generator

from fastapi.testclient import TestClient
from tortoise.contrib.test import finalizer, initializer

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
def event_loop(client: TestClient) -> Generator:
    yield asyncio.get_event_loop()
