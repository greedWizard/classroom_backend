from fastapi.applications import FastAPI
from fastapi.testclient import TestClient

import pytest
from faker import Faker

from core.apps.users.repositories.user_repository import UserRepository
from core.apps.users.services.user_service import UserService
from core.common.exceptions import ServiceError
from core.tests.factories.user.user import UserFactory


@pytest.mark.asyncio
async def test_create_vk_user_success(
    app: FastAPI,
    client: TestClient,
    user_repository: UserRepository,
    user_service: UserService,
    fake: Faker,
):
    await user_repository.count() == 0

    first_name = fake.first_name()
    last_name = fake.last_name()

    user = await user_service.create_user_via_vk(
        vk_user_id=345,
        first_name=first_name,
        last_name=last_name,
        profile_picture_path='',
    )

    assert await user_repository.count() > 0
    assert user
    assert user.first_name == first_name
    assert user.last_name == last_name


@pytest.mark.asyncio
async def test_create_vk_user_success_already_exists_with_vk_id(
    user_service: UserService,
    fake: Faker,
):
    await UserFactory.create(vk_user_id=345)

    first_name = fake.first_name()
    last_name = fake.last_name()

    with pytest.raises(ServiceError):
        await user_service.create_user_via_vk(
            vk_user_id=345,
            first_name=first_name,
            last_name=last_name,
            profile_picture_path='',
        )


@pytest.mark.asyncio
async def test_get_user_created_from_vk_success(user_service: UserService):
    vk_user_id = 345
    await UserFactory.create(vk_user_id=vk_user_id)

    user, _ = await user_service.retrieve(vk_user_id=vk_user_id)
    assert user


@pytest.mark.asyncio
async def test_get_user_created_from_vk_does_not_exist(user_service: UserService):
    user, _ = await user_service.retrieve(vk_user_id=123)
    assert not user
