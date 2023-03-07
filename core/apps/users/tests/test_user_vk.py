from fastapi.applications import FastAPI
from fastapi.testclient import TestClient

import pytest
from faker import Faker

from core.apps.integrations.authentications.vk.schemas import VKResponseUserInfoSchema
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
    fake: Faker,
):
    await user_repository.count()

    vk_user_id = 123
    first_name = fake.first_name()
    last_name = fake.last_name()

    user = await user_service.create_user_via_vk(
        VKResponseUserInfoSchema(
            user_id=vk_user_id,
            first_name=first_name,
            last_name=last_name,
        ),
    )

    assert user
    assert user.first_name == first_name
    assert user.last_name == last_name
