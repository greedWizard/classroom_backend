from typing import List

from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException

from starlette import status

from classroom.schemas import (
    ParticipationCreateByJoinSlugSchema,
    ParticipationSuccessSchema,
    RoomCreateJoinLinkSuccessSchema,
    RoomCreateSchema,
    RoomCreateSuccessSchema,
    RoomDeleteSchema,
    RoomDetailSchema,
    RoomListItemSchema,
    RoomParticipationSchema,
)
from classroom.services.room_service import ParticipationService, RoomService

from user.models import User
from user.schemas import AuthorSchema
from user.dependencies import get_current_user


classroom_router = APIRouter()

@classroom_router.post(
    '',
    response_model=RoomCreateSuccessSchema,
    status_code=status.HTTP_201_CREATED,
    operation_id='createRoom',
)
async def create_new_assignment(
    roomCreateSchema: RoomCreateSchema,
    user: User = Depends(get_current_user),
):
    pass
