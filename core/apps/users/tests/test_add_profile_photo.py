import pytest
from core.tests.client import FastAPITestClient
from core.tests.factories.user import UserFactory

from fastapi import status
from fastapi.applications import FastAPI


@pytest.mark.asyncio
async def test_add_profile_picture_success(
    app: FastAPI,
    client: FastAPITestClient,
):
    user = await UserFactory.create()
    url = app.url_path_for('add_profile_picture')

    with open(
        'core/apps/users/tests/storage/profile_photo.jpeg',
        'rb',
    ) as profile_photo:
        client.authorize(user)
        files = {
            'profile_picture': ('test.jpeg', profile_photo, 'image/jpeg'),
        }
        response = client.post(
            url,
            files=files,
        )

    assert response.status_code == status.HTTP_200_OK

    response_json_data = response.json()
    assert response_json_data['profile_picture_path']


@pytest.mark.asyncio
async def test_add_profile_picture_not_authorized(
    app: FastAPI,
    client: FastAPITestClient,
):
    url = app.url_path_for('add_profile_picture')

    with open(
        'core/apps/users/tests/storage/profile_photo.jpeg',
        'rb',
    ) as profile_photo:
        files = {
            'profile_picture': ('test.jpeg', profile_photo, 'image/jpeg'),
        }
        response = client.post(
            url,
            files=files,
        )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_add_profile_picture_bad_content_type(
    app: FastAPI,
    client: FastAPITestClient,
):
    user = await UserFactory.create()
    url = app.url_path_for('add_profile_picture')

    with open('core/apps/users/tests/storage/bad.txt', 'rb') as profile_photo:
        client.authorize(user)
        files = {
            'profile_picture': ('bad.txt', profile_photo, 'text.plan'),
        }
        response = client.post(
            url,
            files=files,
        )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    json_data = response.json()
    assert json_data['detail'] == {
        'content_type_of_profile_photo': 'Profile photo must be .png, .jpeg, .jpg',
    }


@pytest.mark.asyncio
async def test_change_profile_picture(
    app: FastAPI,
    client: FastAPITestClient,
):
    user = await UserFactory.create()
    client.authorize(user)

    url = app.url_path_for('add_profile_picture')

    with open(
        'core/apps/users/tests/storage/profile_photo.jpeg',
        'rb',
    ) as profile_photo:
        files = {
            'profile_picture': ('test.jpeg', profile_photo, 'image/jpeg'),
        }
        response = client.post(
            url,
            files=files,
        )
    response_json_data = response.json()

    response = client.get(response_json_data['profile_picture_path'])
    response.content

    with open(
        'core/apps/users/tests/storage/new_profile_photo.jpeg',
        'rb',
    ) as profile_photo:
        files = {
            'profile_picture': ('test.jpeg', profile_photo, 'image/jpeg'),
        }
        response = client.post(
            url,
            files=files,
        )

    assert response.ok, response.json()
