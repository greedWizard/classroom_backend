import pytest

from fastapi import status
from fastapi.applications import FastAPI

from apps.classroom.constants import ParticipationRoleEnum
from apps.classroom.repositories.participation_repository import ParticipationRepository
from apps.classroom.repositories.room_repository import RoomRepository
from tests.client import FastAPITestClient
from tests.factories.classroom.participation import ParticipationFactory
from tests.factories.classroom.room import RoomFactory
from tests.factories.user import UserFactory


@pytest.mark.asyncio
async def test_room_create_success(
    app: FastAPI,
    client: FastAPITestClient,
    room_repository: RoomRepository,
    participation_repository: ParticipationRepository,
):
    url = app.url_path_for('create_new_room')
    user = await UserFactory.create()

    assert not await room_repository.fetch()

    room_name = 'fake name'
    description = 'test description'

    client.authorize(user=user)
    response = client.post(
        url,
        json={
            'name': room_name,
            'description': description,
        },
    )
    json_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED, json_data
    room = await room_repository.retrieve(
        name=room_name,
        description=description,
        author_id=user.id,
    )
    assert room
    assert await participation_repository.retrieve(
        user_id=user.id,
        room_id=room.id,
        role=ParticipationRoleEnum.host,
    )


@pytest.mark.asyncio
async def test_room_create_not_logged_in(
    app: FastAPI,
    client: FastAPITestClient,
):
    url = app.url_path_for('create_new_room')

    response = client.post(
        url,
        json={
            'name': 'fake name',
            'description': 'test description',
        },
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_room_refresh_invite_link(
    app: FastAPI,
    client: FastAPITestClient,
    room_repository: RoomRepository,
):
    participation = await ParticipationFactory.create(role=ParticipationRoleEnum.host)
    url = app.url_path_for('refresh_join_slug', room_id=participation.room.id)
    previous_join_slug = participation.room.join_slug

    client.authorize(participation.user)
    response = client.post(url)

    room = await room_repository.refresh(participation.room)
    assert response.status_code == status.HTTP_200_OK
    assert previous_join_slug != room.join_slug


@pytest.mark.asyncio
async def test_join_room_by_link_success(
    app: FastAPI,
    client: FastAPITestClient,
    participation_repository: ParticipationRepository,
):
    room = await RoomFactory.create()
    user = await UserFactory.create()

    client.authorize(user)
    url = app.url_path_for('join_room_by_link', join_slug=room.join_slug)
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

    participation = await participation_repository.retrieve(
        user_id=user.id,
        room_id=room.id,
    )

    assert participation
    assert participation.room_id == room.id
    assert participation.role == ParticipationRoleEnum.participant


@pytest.mark.asyncio
async def test_join_room_by_link_already_in_room(
    app: FastAPI,
    client: FastAPITestClient,
    participation_repository: ParticipationRepository,
):
    participation = await ParticipationFactory.create()
    room = participation.room

    url = app.url_path_for('join_room_by_link', join_slug=room.join_slug)
    client.authorize(participation.user)

    participations_count = await participation_repository.count()

    response = client.get(url)
    json_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST, json_data
    assert await participation_repository.count() == participations_count


@pytest.mark.asyncio
async def test_join_room_by_link_not_logged_in(
    app: FastAPI,
    client: FastAPITestClient,
):
    room = await RoomFactory.create()
    url = app.url_path_for('join_room_by_link', join_slug=room.join_slug)

    response = client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_update_room_success(
    app: FastAPI,
    client: FastAPITestClient,
    room_repository: RoomRepository,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.host,
    )
    room = participation.room
    url = app.url_path_for('update_room', room_id=room.id)

    new_room_name = 'Updated name'
    new_room_description = 'Updated description'

    client.authorize(participation.user)
    response = client.put(
        url,
        json={
            'name': new_room_name,
            'description': new_room_description,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    room = await room_repository.refresh(room)

    assert room.name == new_room_name
    assert room.description == new_room_description


@pytest.mark.asyncio
async def test_update_room_moderator(
    app: FastAPI,
    client: FastAPITestClient,
    room_repository: RoomRepository,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.moderator,
    )
    room = participation.room

    url = app.url_path_for('update_room', room_id=room.id)
    new_room_name = 'Updated name'
    new_room_description = 'Updated description'

    client.authorize(participation.user)
    response = client.put(
        url,
        json={
            'name': new_room_name,
            'description': new_room_description,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    room = await room_repository.refresh(room)

    assert room.name == new_room_name
    assert room.description == new_room_description


@pytest.mark.asyncio
async def test_update_room_participant(
    app: FastAPI,
    client: FastAPITestClient,
    room_repository: RoomRepository,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.participant,
    )
    room = participation.room
    url = app.url_path_for('update_room', room_id=room.id)

    new_room_name = 'Updated name'
    new_room_description = 'Updated description'

    client.authorize(participation.user)
    response = client.put(
        url,
        json={
            'name': new_room_name,
            'description': new_room_description,
        },
    )

    updated_room = await room_repository.refresh(room)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert updated_room.name == room.name
    assert updated_room.description == room.description


@pytest.mark.asyncio
async def test_update_room_not_logged_in(
    app: FastAPI,
    client: FastAPITestClient,
):
    participation = await ParticipationFactory.create()
    room = participation.room

    new_room_name = 'Updated name'
    new_room_description = 'Updated description'

    url = app.url_path_for('update_room', room_id=room.id)
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
    app: FastAPI,
    client: FastAPITestClient,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.participant,
    )
    room = participation.room

    url = app.url_path_for('delete_room', room_id=room.id)
    client.authorize(participation.user)
    response = client.delete(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_delete_room_not_logged_in(
    app: FastAPI,
    client: FastAPITestClient,
):
    room = await RoomFactory.create()
    url = app.url_path_for('delete_room', room_id=room.id)

    response = client.delete(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_room_get_detail(
    app: FastAPI,
    client: FastAPITestClient,
):
    room = await RoomFactory.create()
    participation = await ParticipationFactory.create(
        room=room,
        author=room.author,
        user=room.author,
        role=ParticipationRoleEnum.host,
    )
    client.authorize(participation.user)
    url = app.url_path_for('get_room', room_id=room.id)

    response = client.get(url)
    json_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert json_data['author']['id'] == room.author.id


@pytest.mark.asyncio
async def test_delete_room_success(
    app: FastAPI,
    client: FastAPITestClient,
    participation_repository: ParticipationRepository,
    room_repository: RoomRepository,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.host,
    )
    room = participation.room
    client.authorize(participation.user)
    url = app.url_path_for('delete_room', room_id=room.id)
    print(f'{participation.room_id=} {participation.user_id=}')
    response = client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()
    assert not await room_repository.count()
    assert not await participation_repository.count()
