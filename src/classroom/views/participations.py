from typing import List
from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter

from starlette import status

from classroom.schemas import ParticipationListItemSchema
from classroom.services.participation_service import ParticipationService
from user.models import User
from user.dependencies import get_current_user


participations_router = APIRouter()


@participations_router.get(
    '',
    operation_id='getParticipations',
    response_model=List[ParticipationListItemSchema]
)
async def get_participations(
    room_id: int,
    user: User = Depends(get_current_user),
):
    participation_service = ParticipationService(user)

    participations, errors = await participation_service.fetch({
        'room_id': room_id,
    },
        _select_related=['user', 'room'],
        _ordering=['created_at'],
    )

    if errors:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return [ParticipationListItemSchema.from_orm(participation) \
                for participation in participations]
