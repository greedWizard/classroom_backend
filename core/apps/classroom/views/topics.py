from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from fastapi.exceptions import HTTPException

from starlette import status

from core.apps.classroom.schemas.topics import (
    TopicCreateSchema,
    TopicRetrieveSchema,
    TopicUpdateSchema,
)
from core.apps.classroom.services.topic_service import TopicService
from core.apps.users.dependencies import get_current_user
from core.apps.users.models import User


topic_router = APIRouter()


@topic_router.post(
    '',
    response_model=TopicRetrieveSchema,
    status_code=status.HTTP_201_CREATED,
    operation_id='createTopic',
    summary='Create room lessons topic',
    description='Creates room lessons topic',
)
async def create_topic_handler(
    topic_create_schema: TopicCreateSchema,
    user: User = Depends(get_current_user),
):
    topic_service = TopicService(user)
    topic, errors = await topic_service.create(topic_create_schema)

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return topic


@topic_router.put(
    '/{topic_id}',
    response_model=TopicRetrieveSchema,
    status_code=status.HTTP_201_CREATED,
    operation_id='updateTopic',
    summary='Update room lessons topic',
    description='Updates room lessons topic',
)
async def update_topic_handler(
    topic_id: int,
    topic_update_schema: TopicUpdateSchema,
    user: User = Depends(get_current_user),
):
    topic_service = TopicService(user)
    topic, errors = await topic_service.update(
        id=topic_id,
        update_schema=topic_update_schema,
    )

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return topic


@topic_router.get(
    '',
    response_model=list[TopicRetrieveSchema],
    status_code=status.HTTP_201_CREATED,
    operation_id='fetchRoomTopics',
    summary='Fetch room lessons topic',
    description='Fetches room lessons topic by room_id',
)
async def fetch_room_topics_handler(
    room_id: int = Query(...),
    limit: int = Query(50),
    offset: int = Query(0),
    search: str = Query(None),
    user: User = Depends(get_current_user),
):
    topic_service = TopicService(user)
    topics, errors = await topic_service.fetch_for_room(
        room_id=room_id,
        limit=limit,
        offset=offset,
        search=search,
    )

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return topics


@topic_router.delete(
    '/{topic_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id='deletRoomTopic',
    summary='Delete room lessons topic',
    description='Deletes room lessons topic by topic_id',
)
async def delete_topic_handler(
    topic_id: int,
    user: User = Depends(get_current_user),
):
    topic_service = TopicService(user)
    topics, errors = await topic_service.delete_and_displace_orders(id=topic_id)

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return topics
