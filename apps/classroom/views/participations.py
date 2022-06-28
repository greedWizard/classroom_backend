from typing import List

from starlette import status

from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter

from apps.classroom.schemas import ParticipationListItemSchema
from apps.classroom.schemas.participations import ParticipationDetailSchema
from apps.classroom.services.participation_service import ParticipationService
from apps.user.dependencies import get_current_user
from apps.user.models import User


participations_router = APIRouter()


@participations_router.get(
    '',
    operation_id='getParticipations',
    response_model=List[ParticipationListItemSchema],
)
async def get_participations(
    room_id: int,
    user: User = Depends(get_current_user),
):
    participation_service = ParticipationService(user)

    participations, errors = await participation_service.fetch(
        {
            'room_id': room_id,
        },
        _select_related=['user', 'room'],
        _ordering=['created_at'],
    )

    if errors:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return [
        ParticipationListItemSchema.from_orm(participation)
        for participation in participations
    ]


# TODO: обязательно тесты на эту вьюху
@participations_router.get(
    '/my',
    operation_id='my',
    response_model=ParticipationDetailSchema,
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
    return ParticipationDetailSchema.from_orm(participation)


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
