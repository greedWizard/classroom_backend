from faker import Faker
from fastapi.applications import FastAPI

from fastapi import status
from fastapi.testclient import TestClient
import pytest
import pytest_asyncio
from classroom.constants import HomeWorkAssignmentStatus, ParticipationRoleEnum, RoomPostType

from classroom.models import HomeworkAssignment, Room, Participation, RoomPost
from user.models import User


@pytest_asyncio.fixture
async def room(user: User, fake: Faker):
    room, _ = await Room.get_or_create(
        defaults={
            'id': 1,
            'name': fake.text(),
            'description': fake.text()[:50],
            'text': fake.text(),
            'join_slug': fake.md5(),
            'author': user,
            'updated_by': user,
        }
    )
    await Participation.get_or_create(
        defaults={
            'id': 1,
            'room': room,
            'role': ParticipationRoleEnum.host,
            'user': user,
            'author': user,
            'updated_by': user,
        }
    )
    yield room


@pytest_asyncio.fixture
async def assigned_room_post(room: Room, user: User, fake: Faker):
    room_post, _ = await RoomPost.get_or_create(
        defaults={
            'id': 1,
            'room': room,
            'author': user,
            'title': fake.text(),
            'type': RoomPostType.homework,
            'updated_by': user,
        }
    )
    yield room_post


@pytest.mark.asyncio
async def test_assign_homework_host(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    assigned_room_post: RoomPost,
):
    url = app.url_path_for('assign_homework')
    await Participation.all().update(role=ParticipationRoleEnum.host)

    response = client.post(url, json={
        'assigned_room_post_id': assigned_room_post.id,
    }, headers={
        'Authorization': f'Bearer {authentication_token}'
    })
    json_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json_data == {'detail': {'assigned_room_post_id': \
        "Teacher's can not assign homeworks."}}, json_data


@pytest.mark.asyncio
async def test_assign_homework_not_participant(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    assigned_room_post: RoomPost,
):
    url = app.url_path_for('assign_homework')
    await Participation.all().delete()
    await assigned_room_post.refresh_from_db()

    response = client.post(url, json={
        'assigned_room_post_id': assigned_room_post.id,
    }, headers={
        'Authorization': f'Bearer {authentication_token}'
    })
    json_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json_data == {'detail': {'assigned_room_post_id': \
        'Incorrect post id.'}}, json_data


@pytest.mark.asyncio
async def test_assign_homework_success(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    assigned_room_post: RoomPost,
):
    url = app.url_path_for('assign_homework')
    await Participation.all().update(role=ParticipationRoleEnum.participant)

    response = client.post(url, json={
        'assigned_room_post_id': assigned_room_post.id,
    }, headers={
        'Authorization': f'Bearer {authentication_token}'
    })

    assert response.status_code == status.HTTP_201_CREATED
    await assigned_room_post.refresh_from_db()
    assert await assigned_room_post.assignments.all().first()


@pytest.mark.asyncio
async def test_assign_homework_duplicate(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    assigned_room_post: RoomPost,
):
    url = app.url_path_for('assign_homework')
    await Participation.all().update(role=ParticipationRoleEnum.participant)

    response = client.post(url, json={
        'assigned_room_post_id': assigned_room_post.id,
    }, headers={
        'Authorization': f'Bearer {authentication_token}'
    })
    json_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json_data == {'detail': {'assigned_room_post_id': \
        'Homework is already assigned by this user.'}}, json_data


@pytest.mark.asyncio
async def test_request_changes_when_assigned_not_participating(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
):
    await HomeworkAssignment.all().update(status=HomeWorkAssignmentStatus.assigned)
    await Participation.all().delete()
    assignment = await HomeworkAssignment.first()
    url = app.url_path_for(
        'request_homework_assignment_changes',
        assignment_id=assignment.id,
    )
    comment = 'Переделайте пожалуйста, иначе вам пизда.'

    response = client.post(url, json={
        'comment': comment,
        
    }, headers={
        'Authorization': f'Bearer {authentication_token}'
    })
    json_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST, json_data
    assert json_data == {'detail': 'Invalid assignment.'}


@pytest.mark.asyncio
async def test_request_changes_when_assigned_done(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    assigned_room_post: RoomPost,
):
    await HomeworkAssignment.all().update(status=HomeWorkAssignmentStatus.done)
    await Participation.all().update(role=ParticipationRoleEnum.host)
    assignment = await HomeworkAssignment.first()
    url = app.url_path_for(
        'request_homework_assignment_changes',
        assignment_id=assignment.id,
    )
    comment = 'Переделайте пожалуйста, иначе вам пизда.'

    response = client.post(url, json={
        'comment': comment,
        
    }, headers={
        'Authorization': f'Bearer {authentication_token}'
    })
    json_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST, json_data
    assert json_data == { 'detail': "Can't change assignment now." }


@pytest.mark.asyncio
async def test_request_changes_when_assigned_not_allowed(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    assigned_room_post: RoomPost,
):
    await HomeworkAssignment.all().update(status=HomeWorkAssignmentStatus.assigned)
    await Participation.all().update(role=ParticipationRoleEnum.participant)
    assignment = await HomeworkAssignment.first()
    url = app.url_path_for(
        'request_homework_assignment_changes',
        assignment_id=assignment.id,
    )
    comment = 'Переделайте пожалуйста, иначе вам пизда.'

    response = client.post(url, json={
        'comment': comment,
        
    }, headers={
        'Authorization': f'Bearer {authentication_token}'
    })
    json_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST, json_data
    assert json_data == {'detail': 'You have no permission to do that'}


@pytest.mark.asyncio
async def test_request_changes_when_assigned_success(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    assigned_room_post: RoomPost,
):
    await HomeworkAssignment.all().update(status=HomeWorkAssignmentStatus.assigned)
    await Participation.all().update(role=ParticipationRoleEnum.host)
    assignment = await HomeworkAssignment.first()
    url = app.url_path_for(
        'request_homework_assignment_changes',
        assignment_id=assignment.id,
    )
    comment = 'Переделайте пожалуйста, иначе вам пизда.'

    response = client.post(url, json={
        'comment': comment,
        
    }, headers={
        'Authorization': f'Bearer {authentication_token}'
    })
    json_data = response.json()
    await assignment.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK, json_data
    assert assignment.status == HomeWorkAssignmentStatus.request_changes
    assert assignment.comment == comment


@pytest.mark.asyncio
async def test_mark_success(
    authentication_token: str,
    app: FastAPI,
    client: TestClient,
    assigned_room_post: RoomPost,
):
    await HomeworkAssignment.all().update(status=HomeWorkAssignmentStatus.assigned)
    await Participation.all().update(role=ParticipationRoleEnum.host)
    assignment = await HomeworkAssignment.first()

    url = app.url_path_for('mark_assignment_as_done', assignment_id=assignment.id)
    rate = 3
    comment = '12345'

    response = client.post(url, json={
        'rate': rate,
        'comment': comment,
        
    }, headers={
        'Authorization': f'Bearer {authentication_token}'
    })

    assert response.status_code == status.HTTP_200_OK
    await assignment.refresh_from_db()
    assert assignment.comment == comment
    assert assignment
