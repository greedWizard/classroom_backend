import pytest

from fastapi import status
from fastapi.applications import FastAPI

from apps.classroom.constants import (
    HomeWorkAssignmentStatus,
    ParticipationRoleEnum,
    RoomPostType,
)
from apps.classroom.repositories.assignment import HomeworkAssignmentRepository
from tests.client import FastAPITestClient
from tests.factories.classroom.assignments import AssignmentFactory
from tests.factories.classroom.participation import ParticipationFactory
from tests.factories.classroom.room_post import RoomPostFactory
from tests.factories.user.user import UserFactory


TEST_FILE_PATH = 'new_file.txt'


@pytest.mark.asyncio
async def test_attach_to_post_host(
    app: FastAPI,
    client: FastAPITestClient,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.host,
    )
    post = await RoomPostFactory.create(room=participation.room)

    url = app.url_path_for('create_attachments')
    client.authorize(participation.user)
    files = [
        ('attachments')
    ]
