import asyncio
from faker import Faker
from fastapi.applications import FastAPI

from fastapi import status
from fastapi.testclient import TestClient
import pytest
from classroom.constants import ParticipationRoleEnum, RoomPostType

from classroom.models import RoomPost, Room, Participation

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
    event_loop.run_until_complete(room.fetch_related('room_posts'))
    yield room


@pytest.fixture
def room_post(
    event_loop: asyncio.AbstractEventLoop,
):
    room_post = event_loop.run_until_complete(RoomPost.first())
    yield room_post


def test_room_post_create_success(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
    room_post: RoomPost,
):
    url = app.url_path_for('create_new_room_post')

    assert room
    assert not room_post

    response = client.post(url, json={
        'title': 'fake name',
        'description': 'test description',
        'room_id': room.id,
        'type': RoomPostType.material.name,
    }, headers={
        'Authorization': f'Bearer {authentication_token}'
    })
    
    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert event_loop.run_until_complete(RoomPost.first())


def test_room_post_create_not_logged_in(
    app: FastAPI,
    client: TestClient,
    room: Room,
):
    url = app.url_path_for('create_new_room_post')

    assert room

    response = client.post(url, json={
        'title': 'fake name',
        'description': 'test description',
        'room_id': room.id,
    })
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.json()


def test_room_post_create_not_a_moder(
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
    authentication_token: str,
):
    url = app.url_path_for('create_new_room_post')
    event_loop.run_until_complete(Participation.filter(room_id=room.id)\
        .update(role=ParticipationRoleEnum.participant))

    assert room

    response = client.post(url, json={
        'title': 'fake name',
        'description': 'test description',
        'room_id': room.id,
        'type': RoomPostType.homework.name,
    }, headers={
        'Authorization': f'Bearer {authentication_token}'
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()


def test_room_post_get(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
):
    url = app.url_path_for('get_room_posts')
    assert len(room.room_posts)

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
    room_posts = response.json()['items']
    assert len(room_posts) == len(room.room_posts)


def test_room_post_get_not_a_moder(
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
    room_post: RoomPost,
    authentication_token: str,
):
    url = app.url_path_for('get_room_posts')
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
    room_posts = response.json()['items']
    assert len(room_posts) == len(room.room_posts)


def test_room_post_get_not_in_room(
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
    authentication_token: str,
):
    url = app.url_path_for('get_room_posts')
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


def test_update_room_post_success(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
    room_post: RoomPost,
):
    event_loop.run_until_complete(Participation.filter(room_id=room.id).update(role=ParticipationRoleEnum.host))
    url = app.url_path_for('update_room_post', room_post_id=room_post.id)

    new_room_post_title = 'Updated title'
    new_room_post_description = 'Updated description'
    new_room_post_text = 'updated text'

    response = client.put(url, json={
        'title': new_room_post_title,
        'description': new_room_post_description,
        'text': new_room_post_text,
        'room_id': room.id,
        'type': RoomPostType.material.name,
    }, headers={
        'Authorization': f'Bearer {authentication_token}'
    })

    assert response.status_code == status.HTTP_200_OK, response.json()
    event_loop.run_until_complete(room_post.refresh_from_db())

    assert room_post.title == new_room_post_title
    assert room_post.description == new_room_post_description
    assert room_post.text == new_room_post_text


def test_update_room_post_moderator(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
    room_post: RoomPost,
):
    event_loop.run_until_complete(Participation.filter(room_id=room.id).update(role=ParticipationRoleEnum.moderator))
    url = app.url_path_for('update_room_post', room_post_id=room_post.id)

    new_room_post_title = 'Updated title2'
    new_room_post_description = 'Updated description2'
    new_room_post_text = 'updated text2'

    response = client.put(url, json={
        'title': new_room_post_title,
        'description': new_room_post_description,
        'text': new_room_post_text,
        'room_id': room.id,
        'type': RoomPostType.material.name,
    }, headers={
        'Authorization': f'Bearer {authentication_token}'
    })

    assert response.status_code == status.HTTP_200_OK, response.json()
    event_loop.run_until_complete(room_post.refresh_from_db())

    assert room_post.title == new_room_post_title
    assert room_post.description == new_room_post_description
    assert room_post.text == new_room_post_text


def test_update_room_post_participant(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
    room_post: RoomPost,
):
    event_loop.run_until_complete(Participation.filter(room_id=room.id).update(role=ParticipationRoleEnum.participant))
    url = app.url_path_for('update_room_post', room_post_id=room_post.id)

    new_room_post_title = 'Updated title2'
    new_room_post_description = 'Updated description2'
    new_room_post_text = 'updated text2'

    response = client.put(url, json={
        'title': new_room_post_title,
        'description': new_room_post_description,
        'text': new_room_post_text,
        'room_id': room.id,
        'type': RoomPostType.material.name,
    }, headers={
        'Authorization': f'Bearer {authentication_token}'
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()


def test_update_room_not_logged_in(
    app: FastAPI,
    client: TestClient,
    room_post: RoomPost,
    room: Room,
):
    url = app.url_path_for('update_room_post', room_post_id=room_post.id)

    new_room_post_title = 'Updated title2'
    new_room_post_description = 'Updated description2'
    new_room_post_text = 'updated text2'

    response = client.put(url, json={
        'title': new_room_post_title,
        'description': new_room_post_description,
        'text': new_room_post_text,
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
