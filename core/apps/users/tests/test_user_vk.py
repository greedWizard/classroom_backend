from fastapi.applications import FastAPI
from fastapi.testclient import TestClient

import pytest

from core.apps.users.repositories.user_repository import UserRepository
from core.apps.users.services.user_service import UserService


USER_TEST_PASSWORD = 'testpPassword123'
USER_TEST_UPDATE_PASSWORD = 'testpAssword321'


@pytest.mark.asyncio
async def test_authentication_fail_not_active(
    app: FastAPI,
    client: TestClient,
    user_repository: UserRepository,
    user_service: UserService,
):
    await user_repository.count()
