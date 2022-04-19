import asyncio
import hashlib
from faker import Faker
from fastapi.applications import FastAPI
from fastapi_jwt_auth import AuthJWT

from fastapi import status
from fastapi.testclient import TestClient
import pytest
from classroom.constants import ParticipationRoleEnum

from classroom.models import Material, Room, Participation

from tests.utils.fixtures import client, event_loop, fake, app
from tests.utils.fixtures.users import authentication_token

from user.models import User


@pytest.fixture
def room(
    event_loop: asyncio.AbstractEventLoop,
    fake: Faker,
):
    user= event_loop.run_until_complete(User.first())
    room, _ = event_loop.run_until_complete(Room.get_or_create(
        defaults={
            'id': 1,
            'name': fake.text(),
            'description': fake.text()[:50],
            'text': fake.text(),
            'join_slug': fake.md5(),
            'author': user,
            'updated_by': user,
        }
    ))
    event_loop.run_until_complete(Participation.get_or_create(
        defaults={
            'id': 1,
            'role': ParticipationRoleEnum.host,
            'room': room,
            'author': user,
            'user': user,
            'updated_by': user,
        }
    ))
    event_loop.run_until_complete(room.fetch_related('materials'))
    yield room


@pytest.fixture
def material(
    event_loop: asyncio.AbstractEventLoop,
):
    material = event_loop.run_until_complete(Material.first())
    yield material


def test_material_create_success(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
    material: Material,
):
    url = app.url_path_for('create_new_material')

    assert room
    assert not material

    response = client.post(url, json={
        'title': 'fake name',
        'description': 'test description',
        'room_id': room.id,
    }, headers={
        'Authorization': f'Bearer {authentication_token}'
    })
    
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert event_loop.run_until_complete(Material.first())


def test_material_create_not_logged_in(
    app: FastAPI,
    client: TestClient,
    room: Room,
):
    url = app.url_path_for('create_new_material')

    assert room

    response = client.post(url, json={
        'title': 'fake name',
        'description': 'test description',
        'room_id': room.id,
    })
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.json()


def test_material_create_not_a_moder(
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
    authentication_token: str,
):
    url = app.url_path_for('create_new_material')
    event_loop.run_until_complete(Participation.filter(room_id=room.id)\
        .update(role=ParticipationRoleEnum.participant))

    assert room

    response = client.post(url, json={
        'title': 'fake name',
        'description': 'test description',
        'room_id': room.id,
    }, headers={
        'Authorization': f'Bearer {authentication_token}'
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()


def test_material_get(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
):
    url = app.url_path_for('get_materials')
    assert len(room.materials)

    response = client.get(
        url,
        params={
            'room_id': room.id,
        }, headers={
            'Authorization': f'Bearer {authentication_token}'
        }
    )

    event_loop.run_until_complete(room.refresh_from_db())
    assert response.status_code == status.HTTP_200_OK, response.json()
    materials = response.json()['items']
    assert len(materials) == len(room.materials)


def test_material_get_not_a_moder(
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
    material: Material,
    authentication_token: str,
):
    url = app.url_path_for('get_materials')
    event_loop.run_until_complete(Participation.filter(room_id=room.id)\
        .update(role=ParticipationRoleEnum.participant))

    assert room

    response = client.get(
        url,
        params={
            'room_id': room.id,
        }, headers={
            'Authorization': f'Bearer {authentication_token}'
        }
    )

    event_loop.run_until_complete(room.refresh_from_db())
    assert response.status_code == status.HTTP_200_OK, response.json()
    materials = response.json()['items']
    assert len(materials) == len(room.materials)


def test_material_get_not_in_room(
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
    authentication_token: str,
):
    url = app.url_path_for('get_materials')
    event_loop.run_until_complete(Participation.all().delete())

    assert room

    response = client.get(
        url,
        params={
            'room_id': room.id,
        }, headers={
            'Authorization': f'Bearer {authentication_token}'
        }
    )

    event_loop.run_until_complete(room.refresh_from_db())
    assert response.status_code == status.HTTP_403_FORBIDDEN, response.json()


def test_update_material_success(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
    material: Material,
):
    event_loop.run_until_complete(Participation.filter(room_id=room.id).update(role=ParticipationRoleEnum.host))
    url = app.url_path_for('update_material', material_id=material.id)

    new_material_title = 'Updated title'
    new_material_description = 'Updated description'
    new_material_text = 'updated text'

    response = client.put(url, json={
        'title': new_material_title,
        'description': new_material_description,
        'text': new_material_text,
        'room_id': room.id,
    }, headers={
        'Authorization': f'Bearer {authentication_token}'
    })

    assert response.status_code == status.HTTP_200_OK, response.json()
    event_loop.run_until_complete(material.refresh_from_db())

    assert material.title == new_material_title
    assert material.description == new_material_description
    assert material.text == new_material_text


def test_update_material_moderator(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
    material: Material,
):
    event_loop.run_until_complete(Participation.filter(room_id=room.id).update(role=ParticipationRoleEnum.moderator))
    url = app.url_path_for('update_material', material_id=material.id)

    new_material_title = 'Updated title2'
    new_material_description = 'Updated description2'
    new_material_text = 'updated text2'

    response = client.put(url, json={
        'title': new_material_title,
        'description': new_material_description,
        'text': new_material_text,
        'room_id': room.id,
    }, headers={
        'Authorization': f'Bearer {authentication_token}'
    })

    assert response.status_code == status.HTTP_200_OK, response.json()
    event_loop.run_until_complete(material.refresh_from_db())

    assert material.title == new_material_title
    assert material.description == new_material_description
    assert material.text == new_material_text


def test_update_material_participant(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
    material: Material,
):
    event_loop.run_until_complete(Participation.filter(room_id=room.id).update(role=ParticipationRoleEnum.participant))
    url = app.url_path_for('update_material', material_id=material.id)

    new_material_title = 'Updated title2'
    new_material_description = 'Updated description2'
    new_material_text = 'updated text2'

    response = client.put(url, json={
        'title': new_material_title,
        'description': new_material_description,
        'text': new_material_text,
        'room_id': room.id,
    }, headers={
        'Authorization': f'Bearer {authentication_token}'
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()


def test_update_room_not_logged_in(
    app: FastAPI,
    client: TestClient,
    material: Material,
    room: Room,
):
    url = app.url_path_for('update_material', material_id=material.id)

    new_material_title = 'Updated title2'
    new_material_description = 'Updated description2'
    new_material_text = 'updated text2'

    response = client.put(url, json={
        'title': new_material_title,
        'description': new_material_description,
        'text': new_material_text,
        'room_id': room.id,
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.json()


# def test_delete_room_participant(
#     authentication_token: str,
#     app: FastAPI,
#     client: TestClient,
#     event_loop: asyncio.AbstractEventLoop,
#     room: Room,
# ):
#     event_loop.run_until_complete(Participation.filter(room_id=room.id).update(role=ParticipationRoleEnum.participant))
#     url = app.url_path_for('delete_room', room_id=room.id)

#     response = client.delete(url, headers={
#         'Authorization': f'Bearer {authentication_token}'
#     })

#     assert response.status_code == status.HTTP_400_BAD_REQUEST


# def test_delete_room_not_logged_in(
#     app: FastAPI,
#     client: TestClient,
#     room: Room,
# ):
#     url = app.url_path_for('delete_room', room_id=room.id)

#     response = client.delete(url)
#     assert response.status_code == status.HTTP_401_UNAUTHORIZED


# def test_delete_room_success(
#     authentication_token: str,
#     app: FastAPI,
#     client: TestClient,
#     event_loop: asyncio.AbstractEventLoop,
#     room: Room,
# ):
#     event_loop.run_until_complete(Participation.filter(room_id=room.id).update(role=ParticipationRoleEnum.host))
#     url = app.url_path_for('delete_room', room_id=room.id)

#     response = client.delete(url, headers={
#         'Authorization': f'Bearer {authentication_token}'
#     })

#     assert response.status_code == status.HTTP_204_NO_CONTENT
