from fastapi import status
from fastapi.applications import FastAPI

import pytest

from core.apps.classroom.constants import (
    ParticipationRoleEnum,
    RoomPostType,
)
from core.apps.classroom.repositories.post_repository import RoomPostRepository
from core.apps.classroom.repositories.room_repository import RoomRepository
from core.tests.client import FastAPITestClient
from core.tests.factories.classroom.participation import ParticipationFactory
from core.tests.factories.classroom.room import RoomFactory
from core.tests.factories.classroom.room_post import RoomPostFactory
from core.tests.factories.user.user import UserFactory


@pytest.mark.asyncio
async def test_room_post_create_success(
    app: FastAPI,
    client: FastAPITestClient,
    room_post_repository: RoomPostRepository,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.host,
    )
    user = participation.user
    room = participation.room

    assert not await room_post_repository.count()

    url = app.url_path_for('create_new_room_post')

    assert room

    title = 'fake name'
    description = 'test description'

    client.authorize(user)
    response = client.post(
        url,
        json={
            'title': title,
            'description': description,
            'room_id': room.id,
            'type': RoomPostType.material.name,
        },
    )

    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert await room_post_repository.count()

    room_post = await room_post_repository.retrieve(
        author_id=user.id,
        room_id=room.id,
    )

    assert room_post
    assert room_post.description == description
    assert room_post.title == title


@pytest.mark.asyncio
async def test_room_post_create_not_logged_in(
    app: FastAPI,
    client: FastAPITestClient,
):
    participation = await ParticipationFactory.create()
    room = participation.room

    url = app.url_path_for('create_new_room_post')

    response = client.post(
        url,
        json={
            'title': 'fake name',
            'description': 'test description',
            'room_id': room.id,
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.json()


@pytest.mark.asyncio
async def test_room_post_create_not_a_moder(
    app: FastAPI,
    client: FastAPITestClient,
    room_post_repository: RoomPostRepository,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.participant,
    )
    room = participation.room

    url = app.url_path_for('create_new_room_post')
    client.authorize(participation.user)
    response = client.post(
        url,
        json={
            'title': 'fake name',
            'description': 'test description',
            'room_id': room.id,
            'type': RoomPostType.homework,
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert not await room_post_repository.count()


@pytest.mark.asyncio
async def test_get_room_posts(
    app: FastAPI,
    client: FastAPITestClient,
    room_repository: RoomRepository,
):
    participation = await ParticipationFactory.create()
    room = participation.room
    posts_count = 8
    await RoomPostFactory.create_batch(posts_count, room=room)
    await RoomPostFactory.create_batch(posts_count)

    url = app.url_path_for('get_room_posts')
    client.authorize(participation.user)
    response = client.get(
        url,
        params={
            'room_id': room.id,
        },
    )

    room = await room_repository.refresh(room, join=['posts'])
    assert response.status_code == status.HTTP_200_OK, response.json()
    room_posts = response.json()['items']
    assert len(room_posts) == len(room.posts) == posts_count


@pytest.mark.asyncio
async def test_room_post_get_not_a_moder(
    app: FastAPI,
    client: FastAPITestClient,
    room_repository: RoomRepository,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.participant,
    )
    room = participation.room
    posts_count = 8
    await RoomPostFactory.create_batch(posts_count, room=room)
    await RoomPostFactory.create_batch(posts_count)

    url = app.url_path_for('get_room_posts')
    client.authorize(participation.user)
    response = client.get(
        url,
        params={
            'room_id': room.id,
        },
    )

    room = await room_repository.refresh(room, join=['posts'])
    assert response.status_code == status.HTTP_200_OK, response.json()
    room_posts = response.json()['items']
    assert len(room_posts) == len(room.posts) == posts_count


@pytest.mark.asyncio
async def test_room_post_get_not_in_room(
    app: FastAPI,
    client: FastAPITestClient,
    room_repository: RoomRepository,
):
    room = await RoomFactory.create()
    user = await UserFactory.create()
    await RoomPostFactory.create_batch(10, room=room)

    url = app.url_path_for('get_room_posts')
    client.authorize(user)
    response = client.get(
        url,
        params={
            'room_id': room.id,
        },
    )

    room = await room_repository.refresh(room)
    assert response.status_code == status.HTTP_403_FORBIDDEN, response.json()


@pytest.mark.asyncio
async def test_update_room_post_success(
    app: FastAPI,
    client: FastAPITestClient,
    room_post_repository: RoomPostRepository,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.host,
    )
    room = participation.room
    room_post = await RoomPostFactory.create(room=room)
    user = participation.user

    new_room_post_title = 'Updated title'
    new_room_post_description = 'Updated description'
    new_room_post_text = 'updated text'

    url = app.url_path_for('update_room_post', post_id=room_post.id)
    client.authorize(user)
    response = client.put(
        url,
        json={
            'title': new_room_post_title,
            'description': new_room_post_description,
            'text': new_room_post_text,
            'room_id': room.id,
            'type': RoomPostType.material.name,
        },
    )

    assert response.status_code == status.HTTP_200_OK, response.json()

    room_post = await room_post_repository.refresh(room_post)

    assert room_post.title == new_room_post_title
    assert room_post.description == new_room_post_description
    assert room_post.text == new_room_post_text


@pytest.mark.asyncio
async def test_update_room_post_moderator(
    app: FastAPI,
    client: FastAPITestClient,
    room_post_repository: RoomPostRepository,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.moderator,
    )
    room = participation.room
    room_post = await RoomPostFactory.create(room=room)
    user = participation.user

    new_room_post_title = 'Updated title'
    new_room_post_description = 'Updated description'
    new_room_post_text = 'updated text'

    url = app.url_path_for('update_room_post', post_id=room_post.id)
    client.authorize(user)
    response = client.put(
        url,
        json={
            'title': new_room_post_title,
            'description': new_room_post_description,
            'text': new_room_post_text,
            'room_id': room.id,
            'type': RoomPostType.material.name,
        },
    )

    assert response.status_code == status.HTTP_200_OK, response.json()

    room_post = await room_post_repository.refresh(room_post)

    assert room_post.title == new_room_post_title
    assert room_post.description == new_room_post_description
    assert room_post.text == new_room_post_text


@pytest.mark.asyncio
async def test_update_room_post_participant(
    app: FastAPI,
    client: FastAPITestClient,
    room_post_repository: RoomPostRepository,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.participant,
    )
    room = participation.room
    room_post = await RoomPostFactory.create(room=room)
    user = participation.user

    new_room_post_title = 'Updated title'
    new_room_post_description = 'Updated description'
    new_room_post_text = 'updated text'

    url = app.url_path_for('update_room_post', post_id=room_post.id)
    client.authorize(user)
    response = client.put(
        url,
        json={
            'title': new_room_post_title,
            'description': new_room_post_description,
            'text': new_room_post_text,
            'room_id': room.id,
            'type': RoomPostType.material.name,
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()

    room_post = await room_post_repository.refresh(room_post)

    assert room_post.title != new_room_post_title
    assert room_post.description != new_room_post_description
    assert room_post.text != new_room_post_text


@pytest.mark.asyncio
async def test_update_room_post_not_logged_in(
    app: FastAPI,
    client: FastAPITestClient,
    room_post_repository: RoomPostRepository,
):
    room_post = await RoomPostFactory.create()

    url = app.url_path_for('update_room_post', post_id=room_post.id)

    new_room_post_title = 'Updated title2'
    new_room_post_description = 'Updated description2'
    new_room_post_text = 'updated text2'

    response = client.put(
        url,
        json={
            'title': new_room_post_title,
            'description': new_room_post_description,
            'text': new_room_post_text,
            'room_id': room_post.room_id,
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.json()
    room_post = await room_post_repository.refresh(room_post)
    assert room_post.title != new_room_post_title
    assert room_post.description != new_room_post_description
    assert room_post.text != new_room_post_text


@pytest.mark.asyncio
async def test_delete_room_post_participant(
    app: FastAPI,
    client: FastAPITestClient,
    room_post_repository: RoomPostRepository,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.participant,
    )
    room_post = await RoomPostFactory.create(
        room=participation.room,
    )

    url = app.url_path_for('delete_room_post', post_id=room_post.id)

    client.authorize(participation.user)
    response = client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert await room_post_repository.count()


@pytest.mark.asyncio
async def test_delete_room_post_not_logged_in(
    app: FastAPI,
    client: FastAPITestClient,
):
    room_post = await RoomPostFactory.create()

    url = app.url_path_for('delete_room_post', post_id=room_post.id)

    response = client.delete(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_delete_room_success(
    app: FastAPI,
    client: FastAPITestClient,
    room_post_repository: RoomPostRepository,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.host,
    )
    room_post = await RoomPostFactory.create(
        room=participation.room,
    )

    url = app.url_path_for('delete_room_post', post_id=room_post.id)
    client.authorize(participation.user)
    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not await room_post_repository.count()
