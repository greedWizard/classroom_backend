from typing import List

from starlette import status

from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from fastapi.exceptions import HTTPException

from apps.classroom.schemas import (
    ParticipationCreateByJoinSlugSchema,
    ParticipationSuccessSchema,
    RoomCreateJoinLinkSuccessSchema,
    RoomCreateSchema,
    RoomCreateSuccessSchema,
    RoomDetailSchema,
    RoomListItemSchema,
)
from apps.classroom.services.participation_service import ParticipationService
from apps.classroom.services.room_service import RoomService
from apps.user.dependencies import get_current_user
from apps.user.models import User
from apps.user.schemas import AuthorSchema


classroom_router = APIRouter()


@classroom_router.post(
    '',
    response_model=RoomCreateSuccessSchema,
    status_code=status.HTTP_201_CREATED,
    operation_id='createRoom',
)
async def create_new_room(
    roomCreateSchema: RoomCreateSchema,
    user: User = Depends(get_current_user),
):
    room_service = RoomService(user)
    result, errors = await room_service.create(roomCreateSchema)

    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=errors,
        )
    return result


@classroom_router.put(
    '/{room_id}',
    response_model=RoomDetailSchema,
    status_code=status.HTTP_200_OK,
    operation_id='updateRoom',
)
async def update_room(
    roomUpdateSchema: RoomCreateSchema,
    room_id: int,
    user: User = Depends(get_current_user),
):
    room_service = RoomService(user)
    room, errors = await room_service.update(
        room_id,
        roomUpdateSchema,
        join=['author'],
    )

    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=errors,
        )
    return room


@classroom_router.delete(
    '/{room_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id='deleteRoom',
)
async def delete_room(
    room_id: int,
    user: User = Depends(get_current_user),
):
    room_service = RoomService(user)
    deletes_count, errors = await room_service.delete(id=room_id)

    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=errors,
        )
    if not deletes_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )


@classroom_router.get(
    '/{room_id}',
    response_model=RoomDetailSchema,
    operation_id='getRoom',
)
async def get_room(
    room_id: int,
    user: User = Depends(get_current_user),
):
    room_service = RoomService(user)
    room, errors = await room_service.retrieve(
        id=room_id,
        _join=['participations', 'author'],
    )

    if errors:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=errors)
    return room


@classroom_router.get(
    '',
    response_model=List[RoomListItemSchema],
    operation_id='getCurrentUserRooms',
)
async def current_user_room_list(
    user: User = Depends(get_current_user),
    ordering: List[str] = Query(['-created_at']),
):
    room_service = RoomService(user)
    rooms, errors = await room_service.fetch(_ordering=ordering)

    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=errors,
        )

    room_response_list = []
    participation_service = ParticipationService(user)

    for room in rooms:
        await room.fetch_related('participations', 'author')

        room_response_list.append(
            RoomListItemSchema(
                id=room.id,
                name=room.name,
                description=room.description,
                participations_count=room.participations_count,
                created_at=room.created_at,
                author=AuthorSchema.from_orm(room.author),
                is_moderator=await participation_service.is_user_moderator(
                    room_id=room.id,
                    user_id=user.id,
                ),
            ),
        )
    return room_response_list


@classroom_router.post(
    '/{room_id}/refresh_join_slug',
    response_model=RoomCreateJoinLinkSuccessSchema,
)
async def refresh_join_slug(
    room_id: int,
    user: User = Depends(get_current_user),
):
    room_service = RoomService(user)
    join_slug, errors = await room_service.refresh_join_slug(room_id)

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return RoomCreateJoinLinkSuccessSchema(join_slug=join_slug)


@classroom_router.get(
    '/join/{join_slug}',
    response_model=ParticipationSuccessSchema,
    operation_id='joinBySlug',
)
async def join_room_by_link(
    join_slug: str,
    user: User = Depends(get_current_user),
):
    participation_service = ParticipationService(user)

    participation, errors = await participation_service.create(
        ParticipationCreateByJoinSlugSchema(
            user_id=user.id,
            join_slug=join_slug,
            author_id=user.id,
        ),
    )

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return participation
