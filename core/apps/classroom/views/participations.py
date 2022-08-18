from typing import List

from fastapi import (
    Depends,
    Query,
)
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from fastapi_pagination import (
    Page,
    paginate,
)

from starlette import status

from core.apps.classroom.schemas import ParticipationListItemSchema
from core.apps.classroom.schemas.participations import ParticipationCurrentUserSchema
from core.apps.classroom.services.participation_service import ParticipationService
from core.apps.users.dependencies import get_current_user
from core.apps.users.models import User


participations_router = APIRouter()


@participations_router.get(
    '',
    operation_id='getParticipations',
    response_model=Page[ParticipationListItemSchema],
)
async def get_participations(
    room_id: int,
    user: User = Depends(get_current_user),
    ordering: List[str] = Query(['-created_at']),
):
    participation_service = ParticipationService(user)
    participations, errors = await participation_service.fetch_by_room(
        room_id=room_id,
        _ordering=ordering,
        join=['room', 'room.participations', 'user'],
    )
    if errors:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return paginate(participations)


# TODO: обязательно тесты на эту вьюху
@participations_router.get(
    '/my',
    operation_id='my',
    response_model=ParticipationCurrentUserSchema,
)
async def current_user_participation(
    room_id: int,
    user: User = Depends(get_current_user),
):
    participation_service = ParticipationService(user)

    participation, _ = await participation_service.retrieve(
        room_id=room_id,
        user_id=user.id,
    )

    if not participation:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return participation


# TODO: обязательно тесты на эту вьюху
@participations_router.delete(
    '',
    operation_id='delete',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_participant(
    user_id: int,
    room_id: int,
    user: User = Depends(get_current_user),
):
    participation_service = ParticipationService(user)
    success, errors = await participation_service.remove_user_from_room(
        user_id=user_id,
        room_id=room_id,
    )

    if not success:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=errors)
