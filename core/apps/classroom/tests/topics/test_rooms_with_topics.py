import pytest

from core.apps.classroom.constants import (
    ParticipationRoleEnum,
    RoomPostType,
)
from core.apps.classroom.repositories.post_repository import RoomPostRepository
from core.apps.classroom.repositories.topic_repository import TopicRepository
from core.apps.classroom.schemas.room_posts import (
    RoomPostCreateSchema,
    RoomPostUpdateSchema,
)
from core.apps.classroom.services.room_post_service import RoomPostService
from core.tests.factories.classroom import (
    ParticipationFactory,
    TopicFactory,
)
from core.tests.factories.classroom.room_post import RoomPostFactory


@pytest.mark.asyncio
async def test_set_topic_to_room_success():
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.host,
    )
    topic = await TopicFactory.create(room=participation.room)
    post = await RoomPostFactory.create(room=participation.room)
    post_service = RoomPostService(participation.user)

    post, errors = await post_service.update(
        id=post.id,
        update_schema=RoomPostUpdateSchema(topic_id=topic.id),
    )

    assert not errors, errors
    assert post.topic_id == topic.id, post.topic_id


@pytest.mark.asyncio
async def test_create_post_with_topic_success(
    topic_repository: TopicRepository,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.host,
    )
    topic = await TopicFactory.create(room=participation.room)
    post_service = RoomPostService(participation.user)

    post, errors = await post_service.create(
        create_schema=RoomPostCreateSchema(
            title='My title1',
            topic_id=topic.id,
            type=RoomPostType.material,
            room_id=topic.room_id,
        ),
        join=['topic'],
    )

    topic = await topic_repository.retrieve(
        join=['posts'],
        id=topic.id,
    )

    assert not errors, errors
    assert post.topic_id == topic.id, post.topic
    assert post.topic_id == topic.id, post.topic_id
    assert post.id in [topic_post.id for topic_post in topic.posts]


@pytest.mark.asyncio
async def test_create_post_with_topic_from_other_room():
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.host,
    )
    topic = await TopicFactory.create()
    post_service = RoomPostService(participation.user)

    _, errors = await post_service.create(
        create_schema=RoomPostCreateSchema(
            title='My title1',
            topic_id=topic.id,
            type=RoomPostType.material,
            room_id=participation.room_id,
        ),
        join=['topic'],
    )

    assert errors, errors
    assert 'topic_id' in errors, errors


@pytest.mark.asyncio
async def test_set_topic_from_another_room(
    room_post_repository: RoomPostRepository,
):
    participation = await ParticipationFactory.create(
        role=ParticipationRoleEnum.host,
    )
    topic = await TopicFactory.create()
    post = await RoomPostFactory.create(room=participation.room)
    post_service = RoomPostService(participation.user)

    _, errors = await post_service.update(
        id=post.id,
        update_schema=RoomPostUpdateSchema(topic_id=topic.id),
    )
    post = await room_post_repository.retrieve(id=post.id)

    assert errors, errors
    assert 'topic_id' in errors, errors
    assert not post.topic_id, post.topic_id
