import asyncio

import pytest
import pytest_asyncio

from fastapi import status
from fastapi.applications import FastAPI
from fastapi.testclient import TestClient

from apps.classroom.constants import ParticipationRoleEnum
from apps.classroom.models import (
    Participation,
    Room,
)


@pytest_asyncio.fixture
async def room():
    yield await Room.first()


@pytest.mark.asyncio
async def test_room_create_success(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
):
    url = app.url_path_for('create_new_room')

    assert not room

    response = client.post(
        url,
        json={
            'name': 'fake name',
            'description': 'test description',
        },
        headers={
            'Authorization': f'Bearer {authentication_token}',
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    await Room.first()


@pytest.mark.asyncio
async def test_room_create_not_logged_in(
    app: FastAPI,
    client: TestClient,
):
    url = app.url_path_for('create_new_room')

    response = client.post(
        url,
        json={
            'name': 'fake name',
            'description': 'test description',
        },
        headers={
            'Authorization': f'Bearer fake_token',
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_room_refresh_invite_link(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    room: Room,
):
    url = app.url_path_for('refresh_join_slug', room_id=room.id)
    previous_join_slug = room.join_slug

    response = client.post(
        url,
        headers={
            'Authorization': f'Bearer {authentication_token}',
        },
    )

    await room.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    assert previous_join_slug != room.join_slug


@pytest.mark.asyncio
async def test_join_room_by_link_success(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    room: Room,
):
    await Participation.all().delete()
    url = app.url_path_for('join_room_by_link', join_slug=room.join_slug)

    response = client.get(
        url,
        headers={
            'Authorization': f'Bearer {authentication_token}',
        },
    )

    participation = await Participation.filter(room_id=room.id).first()
    assert response.status_code == status.HTTP_200_OK
    assert participation.room_id == room.id
    assert participation.role == ParticipationRoleEnum.participant


@pytest.mark.asyncio
async def test_join_room_by_link_already_in_room(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    room: Room,
):
    url = app.url_path_for('join_room_by_link', join_slug=room.join_slug)
    participations_count = await Participation.all().count()

    response = client.get(
        url,
        headers={
            'Authorization': f'Bearer {authentication_token}',
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert participations_count == await Participation.all().count()


@pytest.mark.asyncio
async def test_join_room_by_link_not_logged_in(
    app: FastAPI,
    client: TestClient,
    room: Room,
):
    url = app.url_path_for('join_room_by_link', join_slug=room.join_slug)

    response = client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_update_room_success(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    room: Room,
):
    await Participation.filter(room_id=room.id).update(role=ParticipationRoleEnum.host)
    url = app.url_path_for('update_room', room_id=room.id)

    new_room_name = 'Updated name'
    new_room_description = 'Updated description'
    response = client.put(
        url,
        json={
            'name': new_room_name,
            'description': new_room_description,
        },
        headers={
            'Authorization': f'Bearer {authentication_token}',
        },
    )

    assert response.status_code == status.HTTP_200_OK
    await room.refresh_from_db()

    assert room.name == new_room_name
    assert room.description == new_room_description


@pytest.mark.asyncio
async def test_update_room_moderator(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    room: Room,
):
    await Participation.filter(room_id=room.id).update(
        role=ParticipationRoleEnum.moderator,
    )
    url = app.url_path_for('update_room', room_id=room.id)

    new_room_name = 'Updated name'
    new_room_description = 'Updated description'
    response = client.put(
        url,
        json={
            'name': new_room_name,
            'description': new_room_description,
        },
        headers={
            'Authorization': f'Bearer {authentication_token}',
        },
    )

    assert response.status_code == status.HTTP_200_OK
    await room.refresh_from_db()

    assert room.name == new_room_name
    assert room.description == new_room_description


@pytest.mark.asyncio
async def test_update_room_participant(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    room: Room,
):
    await Participation.filter(room_id=room.id).update(
        role=ParticipationRoleEnum.participant,
    )
    url = app.url_path_for('update_room', room_id=room.id)

    new_room_name = 'Updated name'
    new_room_description = 'Updated description'
    response = client.put(
        url,
        json={
            'name': new_room_name,
            'description': new_room_description,
        },
        headers={
            'Authorization': f'Bearer {authentication_token}',
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_update_room_not_logged_in(
    app: FastAPI,
    client: TestClient,
    room: Room,
):
    await Participation.filter(room_id=room.id).update(
        role=ParticipationRoleEnum.participant,
    )
    url = app.url_path_for('update_room', room_id=room.id)

    new_room_name = 'Updated name'
    new_room_description = 'Updated description'
    response = client.put(
        url,
        json={
            'name': new_room_name,
            'description': new_room_description,
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_delete_room_participant(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    room: Room,
):
    await Participation.filter(room_id=room.id).update(
        role=ParticipationRoleEnum.participant,
    )
    url = app.url_path_for('delete_room', room_id=room.id)

    response = client.delete(
        url,
        headers={
            'Authorization': f'Bearer {authentication_token}',
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_delete_room_not_logged_in(
    app: FastAPI,
    client: TestClient,
    room: Room,
):
    url = app.url_path_for('delete_room', room_id=room.id)

    response = client.delete(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_room_get_detail(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    room: Room,
):
    url = app.url_path_for('get_room', room_id=room.id)

    response = client.get(
        url,
        headers={
            'Authorization': f'Bearer {authentication_token}',
        },
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_delete_room_success(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    room: Room,
):
    await Participation.filter(room_id=room.id).update(role=ParticipationRoleEnum.host)
    url = app.url_path_for('delete_room', room_id=room.id)

    response = client.delete(
        url,
        headers={
            'Authorization': f'Bearer {authentication_token}',
        },
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
