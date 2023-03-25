import pytest

from core.apps.classroom.constants import ParticipationRoleEnum
from core.apps.classroom.models.participations import Participation
from core.apps.classroom.repositories.topic_repository import TopicRepository
from core.apps.classroom.schemas.topics import (
    TopicCreateSchema,
    TopicUpdateSchema,
)
from core.apps.classroom.services.topic_service import TopicService
from core.tests.factories.classroom.participation import ParticipationFactory
from core.tests.factories.classroom.topics import TopicFactory


@pytest.mark.asyncio
async def test_create_by_teacher(
    topic_repository: TopicRepository,
):
    teacher_participant = await ParticipationFactory.create(
        role=ParticipationRoleEnum.host,
    )
    previous_topics_count = await topic_repository.count()
    topic_name = 'Урок 1, биология для маслят'

    topic_service = TopicService(teacher_participant.user)

    topic, errors = await topic_service.create(
        create_schema=TopicCreateSchema(
            title=topic_name,
            room_id=teacher_participant.room_id,
        ),
    )

    assert not errors, errors
    assert previous_topics_count + 1 == await topic_repository.count()
    assert topic.order == 0, topic.order

    topic, errors = await topic_service.create(
        create_schema=TopicCreateSchema(
            title=topic_name,
            room_id=teacher_participant.room_id,
        ),
    )

    assert not errors, errors
    assert previous_topics_count + 2 == await topic_repository.count()
    assert topic.order == 1, topic.order


@pytest.mark.asyncio
async def test_create_by_not_teacher(
    topic_repository: TopicRepository,
):
    teacher_participant = await ParticipationFactory.create(
        role=ParticipationRoleEnum.participant,
    )
    previous_topics_count = await topic_repository.count()
    topic_name = 'Урок 1, биология для маслят'
    order = 1

    topic_service = TopicService(teacher_participant.user)

    _, errors = await topic_service.create(
        create_schema=TopicCreateSchema(
            title=topic_name,
            order=order,
            room_id=teacher_participant.room_id,
        ),
    )

    assert errors, errors
    assert 'author' in errors, errors
    assert previous_topics_count == await topic_repository.count()


async def _test_fetch(
    topic_service: TopicService,
    participant: Participation,
    room_id: int,
):
    topics_count = 7
    await TopicFactory.create_batch(size=topics_count, room=participant.room)

    topics, errors = await topic_service.fetch_for_room(
        room_id=room_id,
    )

    assert not errors, errors
    assert len(topics) == topics_count
    assert sorted(topics, key=lambda topic: topic.order) == topics


@pytest.mark.asyncio
async def test_fetch_room_topics_by_teacher():
    participant = await ParticipationFactory.create(
        role=ParticipationRoleEnum.host,
    )
    topic_service = TopicService(participant.user)

    await _test_fetch(topic_service, participant, participant.room_id)


@pytest.mark.asyncio
async def test_fetch_room_topics_by_student():
    participant = await ParticipationFactory.create(
        role=ParticipationRoleEnum.participant,
    )
    topic_service = TopicService(participant.user)

    await _test_fetch(topic_service, participant, participant.room_id)


@pytest.mark.asyncio
async def test_fetch_room_topics_by_other_room_participant():
    teacher_participant = await ParticipationFactory.create(
        role=ParticipationRoleEnum.participant,
    )
    other_room_participants = await ParticipationFactory.create(
        role=ParticipationRoleEnum.participant,
    )
    topic_service = TopicService(other_room_participants.user)

    topics_count = 7
    await TopicFactory.create_batch(size=topics_count, room=teacher_participant.room)

    topics, errors = await topic_service.fetch_for_room(
        room_id=teacher_participant.room_id,
    )

    assert errors, errors
    assert not topics, topics
    assert 'room_id' in errors


@pytest.mark.asyncio
async def test_update_topic_title_by_other_room_participant():
    teacher_participant = await ParticipationFactory.create(
        role=ParticipationRoleEnum.participant,
    )
    other_room_participants = await ParticipationFactory.create(
        role=ParticipationRoleEnum.participant,
    )
    topic_service = TopicService(other_room_participants.user)

    topic = await TopicFactory.create(room=teacher_participant.room)

    _, errors = await topic_service.update(
        id=topic.id,
        update_schema=TopicUpdateSchema(title='silly title', order=topic.order),
    )

    assert errors, errors
    assert 'room_id' in errors


@pytest.mark.asyncio
async def test_update_topic_title_by_student():
    participant = await ParticipationFactory.create(
        role=ParticipationRoleEnum.participant,
    )
    topic_service = TopicService(participant.user)

    topic = await TopicFactory.create(room=participant.room)

    _, errors = await topic_service.update(
        id=topic.id,
        update_schema=TopicUpdateSchema(title='silly title', order=topic.order),
    )

    assert errors, errors
    assert 'author' in errors


@pytest.mark.asyncio
async def test_update_topic_order(
    topic_repository: TopicRepository,
):
    participant = await ParticipationFactory.create(
        role=ParticipationRoleEnum.host,
    )
    topic_service = TopicService(participant.user)

    topics_count = 7
    topics = [
        await TopicFactory.create(
            title=f'topic #{order}',
            order=order,
            room=participant.room,
        ) for order in range(topics_count)
    ]

    new_order = 3
    updated_topic_index = -1

    updated_topic, errors = await topic_service.update(
        id=topics[updated_topic_index].id,
        update_schema=TopicUpdateSchema(title='silly title', order=new_order),
    )

    assert not errors, errors

    room_topics = await topic_repository.fetch_for_room(room_id=participant.room_id)

    assert len(room_topics) == topics_count
    assert room_topics[new_order].id == updated_topic.id

    for diff, next_topic in enumerate(room_topics[new_order + 1:], 1):
        assert next_topic.order > updated_topic.order, updated_topic.order
        assert updated_topic.order + diff == next_topic.order, updated_topic.order


@pytest.mark.asyncio
async def test_fetch_topic_with_search():
    participant = await ParticipationFactory.create(
        role=ParticipationRoleEnum.participant,
    )
    topic_service = TopicService(participant.user)

    topic_title = 'silly title'
    topic = await TopicFactory.create(room=participant.room, title=topic_title)
    await TopicFactory.create(room=participant.room, title='42')

    rooms, _ = await topic_service.fetch_for_room(
        room_id=participant.room.id,
        search='IlLy',
    )

    assert len(rooms) == 1, rooms
    assert rooms[0].id == topic.id


@pytest.mark.asyncio
async def test_delete_topic_as_teacher(
    topic_repository: TopicRepository,
):
    participant = await ParticipationFactory.create(
        role=ParticipationRoleEnum.host,
    )
    topic_service = TopicService(participant.user)

    topic = await TopicFactory.create(room=participant.room)
    previous_topics_count = await topic_repository.count()

    _, errors = await topic_service.delete(id=topic.id)

    assert not errors
    assert previous_topics_count - 1 == await topic_repository.count(), \
        await topic_repository.count()


@pytest.mark.asyncio
async def test_delete_topic_as_participant(
    topic_repository: TopicRepository,
):
    participant = await ParticipationFactory.create(
        role=ParticipationRoleEnum.participant,
    )
    topic_service = TopicService(participant.user)

    topic = await TopicFactory.create(room=participant.room)
    previous_topics_count = await topic_repository.count()

    _, errors = await topic_service.delete_and_displace_orders(id=topic.id)

    assert errors
    assert previous_topics_count == await topic_repository.count(), \
        await topic_repository.count()
