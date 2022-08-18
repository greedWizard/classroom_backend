import pytest
from core.apps.classroom.constants import (
    HomeWorkAssignmentStatus,
    ParticipationRoleEnum,
    RoomPostType,
)
from core.apps.classroom.repositories.assignment import HomeworkAssignmentRepository
from core.tests.client import FastAPITestClient
from core.tests.factories.classroom.assignments import AssignmentFactory
from core.tests.factories.classroom.participation import ParticipationFactory
from core.tests.factories.classroom.room_post import RoomPostFactory
from core.tests.factories.user.user import UserFactory

from fastapi import status
from fastapi.applications import FastAPI


@pytest.mark.asyncio
async def test_assign_homework_host(
    app: FastAPI,
    client: FastAPITestClient,
    assignment_repository: HomeworkAssignmentRepository,
):
    url = app.url_path_for('assign_homework')
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.host,
    )
    room_post = await RoomPostFactory.create(
        room=participation.room,
    )

    client.authorize(participation.user)
    response = client.post(
        url,
        json={
            'post_id': room_post.id,
        },
    )
    json_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST, json_data
    assert not await assignment_repository.count()


@pytest.mark.asyncio
async def test_assign_homework_not_participant(
    app: FastAPI,
    client: FastAPITestClient,
    assignment_repository: HomeworkAssignmentRepository,
):
    url = app.url_path_for('assign_homework')
    user = await UserFactory.create()
    room_post = await RoomPostFactory.create()

    client.authorize(user)
    response = client.post(
        url,
        json={
            'post_id': room_post.id,
        },
    )
    json_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST, json_data
    assert not await assignment_repository.count()


@pytest.mark.asyncio
async def test_assign_homework_to_material(
    app: FastAPI,
    client: FastAPITestClient,
    assignment_repository: HomeworkAssignmentRepository,
):
    url = app.url_path_for('assign_homework')
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.participant,
    )
    room_post = await RoomPostFactory.create(
        room=participation.room,
        type=RoomPostType.material,
    )

    assignments_count = await assignment_repository.count()

    client.authorize(participation.user)
    response = client.post(
        url,
        json={
            'post_id': room_post.id,
        },
    )
    json_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST, json_data
    assert await assignment_repository.count() == assignments_count


@pytest.mark.asyncio
async def test_assign_homework_success(
    app: FastAPI,
    client: FastAPITestClient,
    assignment_repository: HomeworkAssignmentRepository,
):
    url = app.url_path_for('assign_homework')
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.participant,
    )
    room_post = await RoomPostFactory.create(
        room=participation.room,
        type=RoomPostType.homework,
    )

    assignments_count = await assignment_repository.count()

    client.authorize(participation.user)
    response = client.post(
        url,
        json={
            'post_id': room_post.id,
        },
    )
    json_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED, json_data
    assert await assignment_repository.count() > assignments_count

    assignment = await assignment_repository.retrieve(author_id=participation.user.id)

    assert assignment.status == HomeWorkAssignmentStatus.assigned


@pytest.mark.asyncio
async def test_assign_homework_duplicate(
    app: FastAPI,
    client: FastAPITestClient,
):
    url = app.url_path_for('assign_homework')
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.participant,
    )
    post = await RoomPostFactory.create(
        room=participation.room,
        type=RoomPostType.homework,
    )
    await AssignmentFactory.create(post=post, author=participation.user)

    client.authorize(participation.user)
    response = client.post(
        url,
        json={
            'post_id': post.id,
        },
    )
    json_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST, json_data


@pytest.mark.asyncio
async def test_request_changes_when_assigned_not_participating(
    app: FastAPI,
    client: FastAPITestClient,
    assignment_repository: HomeworkAssignmentRepository,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.participant,
    )
    post = await RoomPostFactory.create(
        room=participation.room,
        type=RoomPostType.homework,
    )
    assignment = await AssignmentFactory.create(
        post=post,
        author=participation.user,
        status=HomeWorkAssignmentStatus.assigned,
    )
    user = await UserFactory.create()

    client.authorize(user)
    url = app.url_path_for(
        'request_homework_assignment_changes',
        assignment_id=assignment.id,
    )
    comment = 'Переделайте пожалуйста, иначе вас отчислят.'

    response = client.post(
        url,
        json={
            'comment': comment,
        },
    )
    json_data = response.json()

    updated_assignment = await assignment_repository.refresh(assignment)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, json_data
    assert (
        updated_assignment.status
        == assignment.status
        == HomeWorkAssignmentStatus.assigned
    )


@pytest.mark.asyncio
async def test_request_changes_when_assignment_is_done(
    app: FastAPI,
    client: FastAPITestClient,
    assignment_repository: HomeworkAssignmentRepository,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.host,
    )
    post = await RoomPostFactory.create(
        room=participation.room,
        type=RoomPostType.homework,
    )
    assignment = await AssignmentFactory.create(
        post=post,
        status=HomeWorkAssignmentStatus.done,
    )

    comment = 'Переделайте пожалуйста, иначе вас отчислят.'

    client.authorize(participation.user)
    url = app.url_path_for(
        'request_homework_assignment_changes',
        assignment_id=assignment.id,
    )
    response = client.post(
        url,
        json={
            'comment': comment,
        },
    )
    json_data = response.json()

    updated_assignment = await assignment_repository.refresh(assignment)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, json_data
    assert (
        updated_assignment.status == assignment.status == HomeWorkAssignmentStatus.done
    )


@pytest.mark.asyncio
async def test_request_changes_as_participant(
    app: FastAPI,
    client: FastAPITestClient,
    assignment_repository: HomeworkAssignmentRepository,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.participant,
    )
    post = await RoomPostFactory.create(
        room=participation.room,
        type=RoomPostType.homework,
    )
    assignment = await AssignmentFactory.create(
        post=post,
        status=HomeWorkAssignmentStatus.assigned,
    )

    comment = 'Переделайте пожалуйста, иначе вас отчислят.'

    client.authorize(participation.user)
    url = app.url_path_for(
        'request_homework_assignment_changes',
        assignment_id=assignment.id,
    )
    response = client.post(
        url,
        json={
            'comment': comment,
        },
    )
    json_data = response.json()

    updated_assignment = await assignment_repository.refresh(assignment)
    assert response.status_code == status.HTTP_400_BAD_REQUEST, json_data
    assert (
        updated_assignment.status
        == assignment.status
        == HomeWorkAssignmentStatus.assigned
    )


@pytest.mark.asyncio
async def test_request_changes_when_assigned_success(
    app: FastAPI,
    client: FastAPITestClient,
    assignment_repository: HomeworkAssignmentRepository,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.host,
    )
    post = await RoomPostFactory.create(
        room=participation.room,
        type=RoomPostType.homework,
    )
    assignment = await AssignmentFactory.create(
        post=post,
        status=HomeWorkAssignmentStatus.assigned,
    )

    comment = 'Переделайте пожалуйста, иначе вас отчислят.'

    client.authorize(participation.user)
    url = app.url_path_for(
        'request_homework_assignment_changes',
        assignment_id=assignment.id,
    )
    response = client.post(
        url,
        json={
            'comment': comment,
        },
    )
    json_data = response.json()

    updated_assignment = await assignment_repository.refresh(assignment)
    assert response.status_code == status.HTTP_200_OK, json_data
    assert updated_assignment.status != assignment.status
    assert updated_assignment.status == HomeWorkAssignmentStatus.request_changes
    assert json_data['comment'] == comment


@pytest.mark.asyncio
async def test_mark_success(
    app: FastAPI,
    client: FastAPITestClient,
    assignment_repository: HomeworkAssignmentRepository,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.host,
    )
    post = await RoomPostFactory.create(
        room=participation.room,
        type=RoomPostType.homework,
    )
    assignment = await AssignmentFactory.create(
        post=post,
        status=HomeWorkAssignmentStatus.assigned,
    )

    comment = 'Отличная работа, Олег.'
    rate = 5

    client.authorize(participation.user)
    url = app.url_path_for(
        'mark_assignment_as_done',
        assignment_id=assignment.id,
    )
    response = client.post(
        url,
        json={
            'rate': rate,
            'comment': comment,
        },
    )
    json_data = response.json()

    updated_assignment = await assignment_repository.refresh(assignment)
    assert response.status_code == status.HTTP_200_OK, json_data
    assert updated_assignment.status != assignment.status
    assert updated_assignment.status == HomeWorkAssignmentStatus.done
    assert json_data['comment'] == comment


@pytest.mark.asyncio
async def test_get_assignment_success(
    app: FastAPI,
    client: FastAPITestClient,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.host,
    )
    post = await RoomPostFactory.create(room=participation.room)
    assignment = await AssignmentFactory.create(
        post=post,
    )

    client.authorize(participation.user)
    url = app.url_path_for('get_assignment', assignment_id=assignment.id)
    response = client.get(url)
    json_data = response.json()

    assert response.status_code == status.HTTP_200_OK, json_data


@pytest.mark.asyncio
async def test_get_my_assignment_in_post_success(
    app: FastAPI,
    client: FastAPITestClient,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.participant,
    )
    post = await RoomPostFactory.create(room=participation.room)
    assignment = await AssignmentFactory.create(
        post=post,
        author=participation.user,
    )

    client.authorize(participation.user)
    url = app.url_path_for('get_my_assignment', post_id=post.id)
    response = client.get(url)
    json_data = response.json()

    assert response.status_code == status.HTTP_200_OK, json_data
    assert json_data['id'] == assignment.id


@pytest.mark.asyncio
async def test_get_post_assignments_teacher(
    app: FastAPI,
    client: FastAPITestClient,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.host,
    )
    assignments_count = 10
    post = await RoomPostFactory.create(room=participation.room)

    for _ in range(assignments_count):
        await AssignmentFactory.create(post=post)

    client.authorize(participation.user)
    url = app.url_path_for('fetch_assignments')
    response = client.get(url, params={'post_id': post.id})
    json_data = response.json()

    assert response.status_code == status.HTTP_200_OK, json_data
    assert json_data['total'] == assignments_count


@pytest.mark.asyncio
async def test_reassign_homework_success(
    app: FastAPI,
    client: FastAPITestClient,
    assignment_repository: HomeworkAssignmentRepository,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.host,
    )
    post = await RoomPostFactory.create(room=participation.room)
    assignment = await AssignmentFactory.create(
        post=post,
        author=participation.user,
        status=HomeWorkAssignmentStatus.request_changes,
    )

    client.authorize(participation.user)
    url = app.url_path_for('reassign_homework', assignment_id=assignment.id)
    response = client.post(url)
    json_data = response.json()

    assert response.status_code == status.HTTP_200_OK, json_data
    updated_assignment = await assignment_repository.refresh(assignment)
    assert updated_assignment.status == HomeWorkAssignmentStatus.assigned


@pytest.mark.asyncio
async def test_reassign_homework_did_not_request_changes(
    app: FastAPI,
    client: FastAPITestClient,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.host,
    )
    post = await RoomPostFactory.create(room=participation.room)
    assignment = await AssignmentFactory.create(
        post=post,
        author=participation.user,
        status=HomeWorkAssignmentStatus.done,
    )

    client.authorize(participation.user)
    url = app.url_path_for('reassign_homework', assignment_id=assignment.id)
    response = client.post(url)
    json_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST, json_data


@pytest.mark.asyncio
async def test_get_post_assignments_participant(
    app: FastAPI,
    client: FastAPITestClient,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.participant,
    )
    post = await RoomPostFactory.create(room=participation.room)
    await AssignmentFactory.create(post=post)

    client.authorize(participation.user)
    url = app.url_path_for('fetch_assignments')
    response = client.get(url, params={'post_id': post.id})
    json_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST, json_data


@pytest.mark.asyncio
async def test_get_room_assignments_teacher(
    app: FastAPI,
    client: FastAPITestClient,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.host,
    )
    assignments_count = 10

    for _ in range(assignments_count):
        post = await RoomPostFactory.create(room=participation.room)
        await AssignmentFactory.create(post=post)

    client.authorize(participation.user)
    url = app.url_path_for('fetch_assignments')
    response = client.get(url, params={'room_id': participation.room.id})
    json_data = response.json()

    assert response.status_code == status.HTTP_200_OK, json_data
    assert json_data['total'] == assignments_count


@pytest.mark.asyncio
async def test_get_room_assignments_participant(
    app: FastAPI,
    client: FastAPITestClient,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.participant,
    )
    student_assignments_count = 5

    for _ in range(student_assignments_count):
        post = await RoomPostFactory.create(room=participation.room)
        await AssignmentFactory.create(post=post, author=participation.user)
    for _ in range(student_assignments_count):
        post = await RoomPostFactory.create(room=participation.room)
        await AssignmentFactory.create(post=post)

    client.authorize(participation.user)
    url = app.url_path_for('fetch_assignments')
    response = client.get(url, params={'room_id': participation.room.id})
    json_data = response.json()

    assert response.status_code == status.HTTP_200_OK, json_data
    assert json_data['total'] == student_assignments_count
