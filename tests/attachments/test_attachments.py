import tempfile
from os import stat
import pytest

from fastapi import status
from fastapi.applications import FastAPI

from mock import mock_open, MagicMock
from mock import Mock, patch
from io import BytesIO


from apps.attachment.repositories.attachment_repository import AttachmentRepository
from apps.classroom.constants import ParticipationRoleEnum
from apps.classroom.repositories.assignment import HomeworkAssignmentRepository
from apps.classroom.repositories.post_repository import RoomPostRepository
from tests.client import FastAPITestClient
from tests.factories.classroom.assignments import AssignmentFactory
from tests.factories.classroom.participation import ParticipationFactory
from tests.factories.classroom.room_post import RoomPostFactory
from tests.utils.functions import check_attachment_is_attached

from apps.common.config import config


TEST_FILE_PATH = 'tests/attachments/new_file.txt'


@pytest.mark.asyncio
async def test_attach_to_post_host(
    app: FastAPI,
    client: FastAPITestClient,
    attachment_repository: AttachmentRepository,
    room_post_repository: RoomPostRepository,
):
    assert not await attachment_repository.count()
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.host,
    )
    post = await RoomPostFactory.create(room=participation.room)
    url = app.url_path_for('create_attachments')

    with open(TEST_FILE_PATH, 'rb') as upload_file:
        client.authorize(participation.user)
        files = files = {
            'attachments': ('new_file.txt', upload_file, 'text/plain'),
        }
        response = client.post(
            url=url,
            files=files,
            params={
                'room_id': post.room.id,
                'post_id': post.id,
            },
        )

    json_data = response.json()
    assert response.status_code == status.HTTP_201_CREATED, json_data
    assert not json_data['errors']

    attachment = await attachment_repository.retrieve(post_id=post.id)
    room_post = await room_post_repository.retrieve(id=post.id, join=['attachments'])

    check_attachment_is_attached(
        attachment=attachment,
        attached_to=room_post,
        file_path=TEST_FILE_PATH,
    )


@pytest.mark.asyncio
async def test_attach_to_post_participant(
    app: FastAPI,
    client: FastAPITestClient,
    attachment_repository: AttachmentRepository,
):
    assert not await attachment_repository.count()
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.participant,
    )
    post = await RoomPostFactory.create(room=participation.room)
    url = app.url_path_for('create_attachments')

    with open(TEST_FILE_PATH, 'rb') as upload_file:
        client.authorize(participation.user)
        files = files = {
            'attachments': ('new_file.txt', upload_file, 'text/plain'),
        }
        response = client.post(
            url=url,
            files=files,
            params={
                'room_id': post.room.id,
                'post_id': post.id,
            },
        )
    json_data = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST, json_data
    assert json_data.get('detail')


@pytest.mark.asyncio
async def test_attach_to_assignment_participant_not_author(
    app: FastAPI,
    client: FastAPITestClient,
    attachment_repository: AttachmentRepository,
):
    assert not await attachment_repository.count()

    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.participant,
    )
    post = await RoomPostFactory.create(room=participation.room)
    assignment = await AssignmentFactory.create(post=post)
    url = app.url_path_for('create_attachments')

    with open(TEST_FILE_PATH, 'rb') as upload_file:
        client.authorize(participation.user)
        files = files = {
            'attachments': ('new_file.txt', upload_file, 'text/plain'),
        }
        response = client.post(
            url=url,
            files=files,
            params={
                'room_id': assignment.post.room_id,
                'assignment_id': assignment.id,
            },
        )
    json_data = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST, json_data
    assert json_data.get('detail')


@pytest.mark.asyncio
async def test_attach_to_assignment_participant_author(
    app: FastAPI,
    client: FastAPITestClient,
    attachment_repository: AttachmentRepository,
    assignment_repository: HomeworkAssignmentRepository,
):
    assert not await attachment_repository.count()

    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.participant,
    )
    post = await RoomPostFactory.create(room=participation.room)
    assignment = await AssignmentFactory.create(post=post, author=participation.user)
    url = app.url_path_for('create_attachments')

    with open(TEST_FILE_PATH, 'rb') as upload_file:
        client.authorize(participation.user)
        files = files = {
            'attachments': ('new_file.txt', upload_file, 'text/plain'),
        }
        response = client.post(
            url=url,
            files=files,
            params={
                'assignment_id': assignment.id,
            },
        )
    json_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED, json_data
    assert not json_data.get('detail')

    attachment = await attachment_repository.retrieve(assignment_id=assignment.id)
    assignment = await assignment_repository.retrieve(
        id=assignment.id, join=['attachments']
    )

    check_attachment_is_attached(
        attachment=attachment,
        attached_to=assignment,
        file_path=TEST_FILE_PATH,
    )


@pytest.mark.asyncio
async def test_attach_to_assignment_participant_moderator(
    app: FastAPI,
    client: FastAPITestClient,
    attachment_repository: AttachmentRepository,
):
    assert not await attachment_repository.count()

    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.moderator,
    )
    post = await RoomPostFactory.create(room=participation.room)
    assignment = await AssignmentFactory.create(post=post)
    url = app.url_path_for('create_attachments')

    with open(TEST_FILE_PATH, 'rb') as upload_file:
        client.authorize(participation.user)
        files = files = {
            'attachments': ('new_file.txt', upload_file, 'text/plain'),
        }
        response = client.post(
            url=url,
            files=files,
            params={
                'room_id': assignment.post.room_id,
                'assignment_id': assignment.id,
            },
        )
    json_data = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST, json_data
    assert json_data.get('detail')


@pytest.mark.asyncio
async def test_attach_file_assignment_or_post_id_not_provided(
    app: FastAPI,
    client: FastAPITestClient,
    attachment_repository: AttachmentRepository,
):
    assert not await attachment_repository.count()

    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.moderator,
    )
    url = app.url_path_for('create_attachments')

    with open(TEST_FILE_PATH, 'rb') as upload_file:
        client.authorize(participation.user)
        files = files = {
            'attachments': ('new_file.txt', upload_file, 'text/plain'),
        }
        response = client.post(url=url, files=files)
    json_data = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST, json_data
    assert json_data.get('detail')


@pytest.mark.asyncio
async def test_attachment_file_is_large(
    app: FastAPI,
    client: FastAPITestClient,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.moderator,
    )
    post = await RoomPostFactory.create(room=participation.room)
    url = app.url_path_for('create_attachments')
    check_file_size_mock = Mock()
    check_file_size_mock.return_value = True

    with patch(
            'apps.attachment.services.attachment_service.AttachmentService._check_file_size',
            check_file_size_mock,
    ):
        with tempfile.TemporaryFile() as file:
            client.authorize(participation.user)
            files = {
                'attachments': ('file.txt', file, 'text/plan'),
            }

            response = client.post(
                url=url,
                files=files,
                params={
                    'room_id': post.room.id,
                    'post_id': post.id,
                },
            )

    json_data = response.json()
    assert response.status_code == status.HTTP_400_BAD_REQUEST, json_data
    assert json_data['detail'] == [{'source': 'file.txt size is to large'}]
