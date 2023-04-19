from fastapi import FastAPI

import pytest
from starlette import status

from core.apps.classroom.models.room_posts import RoomPost
from core.tests.client import FastAPITestClient
from core.tests.factories.classroom.participation import ParticipationFactory
from core.tests.factories.classroom.room_post import RoomPostFactory
from core.tests.factories.classroom.topics import TopicFactory


async def assert_posts_matched(
    response_data: dict,
    response_status_code: int,
    asserting_posts_list: list[RoomPost],
):
    assert response_status_code == status.HTTP_200_OK, response_data
    assert len(response_data) == len(asserting_posts_list), response_data

    for post_data in response_data:
        assert post_data['id'] in (post.id for post in asserting_posts_list)


@pytest.mark.asyncio
async def test_fetch_posts_with_topics(
    app: FastAPI,
    client: FastAPITestClient,
):
    participation = await ParticipationFactory.create()
    client.authorize(participation.user)

    topic = await TopicFactory.create()
    posts_with_topics_count, posts_without_topics_count = 3, 4
    posts_with_topics = await RoomPostFactory.create_batch(
        posts_with_topics_count,
        room=participation.room,
        topic=topic,
    )
    posts_without_topics = await RoomPostFactory.create_batch(
        posts_without_topics_count,
        room=participation.room,
    )

    url = app.url_path_for('get_room_posts')

    response = client.get(
        url=url,
        params={
            'room_id': participation.room_id,
        },
    )
    response_data = response.json()

    await assert_posts_matched(
        response_data,
        response.status_code,
        posts_with_topics + posts_without_topics,
    )

    response = client.get(
        url=url,
        params={
            'topic_id': topic.id,
            'room_id': participation.room_id,
        },
    )
    response_data = response.json()

    await assert_posts_matched(
        response_data,
        response.status_code,
        posts_with_topics,
    )
