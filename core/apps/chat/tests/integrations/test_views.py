from fastapi import FastAPI

import pytest
from starlette import status

from core.apps.chat.repositories.dialog_repository import DialogRepository
from core.tests.client import FastAPITestClient
from core.tests.factories.chat.dialog import DialogFactory
from core.tests.factories.classroom.participation import ParticipationFactory
from core.tests.factories.classroom.room import RoomFactory


@pytest.mark.asyncio
async def test_start_dialog_not_roommates(
    app: FastAPI,
    client: FastAPITestClient,
    dialog_repository: DialogRepository,
):
    participations = await ParticipationFactory.create_batch(size=2)

    url = app.url_path_for('start_dialog')
    client.authorize(participations[0].user)
    response = client.post(
        url=url, json={
            'participants_ids': [participation.user_id for participation in participations],
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
    assert response.json() == {'detail': {'error': 'Users are not rommates.'}}
    assert not await dialog_repository.count()


@pytest.mark.asyncio
async def test_start_dialog_success(
    app: FastAPI,
    client: FastAPITestClient,
    dialog_repository: DialogRepository,
):
    room = await RoomFactory.create()
    participations = await ParticipationFactory.create_batch(size=2, room=room)

    url = app.url_path_for('start_dialog')
    client.authorize(participations[0].user)

    response = client.post(
        url=url, json={
            'participants_ids': [participation.user_id for participation in participations[1:]],
        },
    )

    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert await dialog_repository.count()


@pytest.mark.asyncio
async def test_start_dialog_repeat(
    app: FastAPI,
    client: FastAPITestClient,
    dialog_repository: DialogRepository,
):
    room = await RoomFactory.create()
    participations = await ParticipationFactory.create_batch(size=2, room=room)
    await DialogFactory.create(participants=[participation.user for participation in participations])

    url = app.url_path_for('start_dialog')
    client.authorize(participations[0].user)

    dialogs_count = await dialog_repository.count()

    response = client.post(
        url=url, json={
            'participants_ids': [participation.user_id for participation in participations[1:]],
        },
    )

    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert await dialog_repository.count() == dialogs_count
