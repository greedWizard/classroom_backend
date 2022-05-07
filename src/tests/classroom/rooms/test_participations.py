import asyncio
from fastapi.applications import FastAPI

from fastapi import status
from fastapi.testclient import TestClient
import pytest
from classroom.constants import ParticipationRoleEnum

from classroom.models import Room, Participation

from user.models import User


@pytest.fixture
def room(
    event_loop: asyncio.AbstractEventLoop,
    user: User,
) -> Room:
    return event_loop.run_until_complete(
        Room.get_or_create(
            defaults={
                'name': 'fake room',
                'author': user,
                'updated_by': user,
                'join_slug': 'fake_join_slug',
            },
            id=1,
        )
    )[0]

def test_participations_not_found(
    app: FastAPI,
    client: FastAPI,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
    authentication_token: str,
) -> Room:
    url = app.url_path_for('get_participations')
    
    response = client.get(url, headers={
        'Authorization': f'Bearer {authentication_token}'
    }, params={
        'room_id': room.id,
    })

    assert response.status_code == status.HTTP_200_OK, response.status_code
    assert not response.json(), response.json()


def test_participations_not_found(
    app: FastAPI,
    client: FastAPI,
    event_loop: asyncio.AbstractEventLoop,
    room: Room,
    authentication_token: str,
    user: User,
) -> Room:
    url = app.url_path_for('get_participations')

    event_loop.run_until_complete(
        Participation.create(
            room_id=room.id,
            user_id=user.id,
            author=user,
            updated_by=user,
        )
    )

    response = client.get(url, headers={
        'Authorization': f'Bearer {authentication_token}'
    }, params={
        'room_id': room.id,
    })

    assert response.status_code == status.HTTP_200_OK
