import asyncio
import hashlib
from faker import Faker
from fastapi.applications import FastAPI
from fastapi_jwt_auth import AuthJWT

from fastapi import status
from fastapi.testclient import TestClient
import pytest
from classroom.constants import ParticipationRoleEnum

from classroom.models import Room, Participation



@pytest.fixture
def room(
    event_loop: asyncio.AbstractEventLoop
):
    yield event_loop.run_until_complete(Room.first())


def test_room_create_success(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
):
    url = app.url_path_for('create_new_room')

    assert not room

    response = client.post(url, json={
        'name': 'fake name',
        'description': 'test description',
    }, headers={
        'Authorization': f'Bearer {authentication_token}'
    })

    assert response.status_code == status.HTTP_201_CREATED
    assert event_loop.run_until_complete(Room.first())


def test_room_create_not_logged_in(
    app: FastAPI,
    client: TestClient,
):
    url = app.url_path_for('create_new_room')

    response = client.post(url, json={
        'name': 'fake name',
        'description': 'test description',
    }, headers={
        'Authorization': f'Bearer fake_token'
    })

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_room_refresh_invite_link(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
):
    url = app.url_path_for('refresh_join_slug', room_id=room.id)
    previous_join_slug = room.join_slug

    response = client.post(url, headers={
        'Authorization': f'Bearer {authentication_token}'
    })

    event_loop.run_until_complete(room.refresh_from_db())
    assert response.status_code == status.HTTP_200_OK
    assert previous_join_slug != room.join_slug


def test_join_room_by_link_success(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
):
    event_loop.run_until_complete(Participation.all().delete())
    url = app.url_path_for('join_room_by_link', join_slug=room.join_slug)

    response = client.get(url, headers={
        'Authorization': f'Bearer {authentication_token}'
    })

    participation = event_loop.run_until_complete(Participation.filter(room_id=room.id).first())
    assert response.status_code == status.HTTP_200_OK
    assert participation.room_id == room.id
    assert participation.role == ParticipationRoleEnum.participant


def test_join_room_by_link_already_in_room(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
):
    url = app.url_path_for('join_room_by_link', join_slug=room.join_slug)
    participations_count = event_loop.run_until_complete(Participation.all().count())

    response = client.get(url, headers={
        'Authorization': f'Bearer {authentication_token}'
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert participations_count == event_loop.run_until_complete(Participation.all().count())


def test_join_room_by_link_not_logged_in(
    app: FastAPI,
    client: TestClient,
    room: Room,
):
    url = app.url_path_for('join_room_by_link', join_slug=room.join_slug)

    response = client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_room_success(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
):
    event_loop.run_until_complete(Participation.filter(room_id=room.id).update(role=ParticipationRoleEnum.host))
    url = app.url_path_for('update_room', room_id=room.id)

    new_room_name = 'Updated name'
    new_room_description = 'Updated description'
    response = client.put(url, json={
        'name': new_room_name,
        'description': new_room_description,
    }, headers={
        'Authorization': f'Bearer {authentication_token}'
    })

    assert response.status_code == status.HTTP_200_OK
    event_loop.run_until_complete(room.refresh_from_db())

    assert room.name == new_room_name
    assert room.description == new_room_description


def test_update_room_moderator(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
):
    event_loop.run_until_complete(Participation.filter(room_id=room.id).update(role=ParticipationRoleEnum.moderator))
    url = app.url_path_for('update_room', room_id=room.id)

    new_room_name = 'Updated name'
    new_room_description = 'Updated description'
    response = client.put(url, json={
        'name': new_room_name,
        'description': new_room_description,
    }, headers={
        'Authorization': f'Bearer {authentication_token}'
    })

    assert response.status_code == status.HTTP_200_OK
    event_loop.run_until_complete(room.refresh_from_db())

    assert room.name == new_room_name
    assert room.description == new_room_description


def test_update_room_participant(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
):
    event_loop.run_until_complete(Participation.filter(room_id=room.id).update(role=ParticipationRoleEnum.participant))
    url = app.url_path_for('update_room', room_id=room.id)

    new_room_name = 'Updated name'
    new_room_description = 'Updated description'
    response = client.put(url, json={
        'name': new_room_name,
        'description': new_room_description,
    }, headers={
        'Authorization': f'Bearer {authentication_token}'
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_update_room_not_logged_in(
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
):
    event_loop.run_until_complete(Participation.filter(room_id=room.id).update(role=ParticipationRoleEnum.participant))
    url = app.url_path_for('update_room', room_id=room.id)

    new_room_name = 'Updated name'
    new_room_description = 'Updated description'
    response = client.put(url, json={
        'name': new_room_name,
        'description': new_room_description,
    })

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_room_participant(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
):
    event_loop.run_until_complete(Participation.filter(room_id=room.id).update(role=ParticipationRoleEnum.participant))
    url = app.url_path_for('delete_room', room_id=room.id)

    response = client.delete(url, headers={
        'Authorization': f'Bearer {authentication_token}'
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_delete_room_not_logged_in(
    app: FastAPI,
    client: TestClient,
    room: Room,
):
    url = app.url_path_for('delete_room', room_id=room.id)

    response = client.delete(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_room_get_detail(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    room: Room,
):
    url = app.url_path_for('get_room', room_id=room.id)

    response = client.get(url, headers={
        'Authorization': f'Bearer {authentication_token}'
    })

    assert response.status_code == status.HTTP_200_OK


def test_delete_room_success(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
):
    event_loop.run_until_complete(Participation.filter(room_id=room.id).update(role=ParticipationRoleEnum.host))
    url = app.url_path_for('delete_room', room_id=room.id)

    response = client.delete(url, headers={
        'Authorization': f'Bearer {authentication_token}'
    })

    assert response.status_code == status.HTTP_204_NO_CONTENT
