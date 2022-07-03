from typing import List

from fastapi_pagination import (
    Page,
    paginate,
)
from starlette import status

from fastapi import (
    APIRouter,
    Depends,
    Query,
    UploadFile,
)
from fastapi.exceptions import HTTPException

from apps.attachment.schemas import (
    AttachmentCreateSchema,
    AttachmentListItemSchema,
)
from apps.attachment.services.attachment_service import AttachmentService
from apps.classroom.schemas import (
    RoomPostCreateSchema,
    RoomPostCreateSuccessSchema,
    RoomPostDeleteSchema,
    RoomPostDetailSchema,
    RoomPostUpdateSchema,
)
from apps.classroom.schemas.common import RoomPostListItemSchema
from apps.classroom.services.room_post_service import RoomPostService
from apps.classroom.utils import make_room_post_schema
from apps.user.dependencies import get_current_user
from apps.user.models import User


room_posts_router = APIRouter()


@room_posts_router.post(
    '',
    response_model=RoomPostCreateSuccessSchema,
    status_code=status.HTTP_201_CREATED,
    operation_id='createRoomPost',
)
async def create_new_room_post(
    room_postCreateSchema: RoomPostCreateSchema,
    user: User = Depends(get_current_user),
):
    room_post_service = RoomPostService(user)
    room_post, errors = await room_post_service.create(room_postCreateSchema)

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return room_post


@room_posts_router.put(
    '/{post_id}',
    response_model=RoomPostDetailSchema,
    status_code=status.HTTP_200_OK,
    operation_id='updateRoomPost',
)
async def update_room_post(
    post_id: int,
    room_postUpdateSchema: RoomPostUpdateSchema,
    user: User = Depends(get_current_user),
):
    room_post_service = RoomPostService(user)
    room_post, errors = await room_post_service.update(
        post_id,
        room_postUpdateSchema,
        join=['author', 'room', 'attachments'],
    )

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return room_post


@room_posts_router.get(
    '',
    response_model=Page[RoomPostListItemSchema],
    status_code=status.HTTP_200_OK,
    operation_id='getRoomPosts',
)
async def get_room_posts(
    room_id: int,
    user: User = Depends(get_current_user),
    ordering: List[str] = Query(['-created_at']),
):
    room_post_service = RoomPostService(user)
    room_posts, errors = await room_post_service.fetch(
        _ordering=ordering,
        room_id=room_id,
        join=['author', 'attachments'],
    )

    if errors:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=errors)
    return paginate(room_posts)


@room_posts_router.get(
    '/{post_id}',
    response_model=RoomPostDetailSchema,
    status_code=status.HTTP_200_OK,
    operation_id='getRoomPost',
)
async def get_room_post(
    post_id: int,
    user: User = Depends(get_current_user),
):
    room_post_service = RoomPostService(user)
    room_post, errors = await room_post_service.retrieve(
        ['author', 'attachments'],
        id=post_id,
    )

    if errors:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=errors)
    return await make_room_post_schema(room_post)


@room_posts_router.post(
    '/{post_id}/attachments',
    response_model=List[AttachmentListItemSchema],
    status_code=status.HTTP_201_CREATED,
    operation_id='attachFilesToRoomPost',
)
async def attach_files_to_room_post(
    post_id: int,
    attachments: List[UploadFile],
    user: User = Depends(get_current_user),
):
    attachments_list = []
    attachment_service = AttachmentService(user)

    for attachment in attachments:
        attachments_list.append(
            AttachmentCreateSchema(
                filename=attachment.filename,
                source=await attachment.read(),
            ),
        )
    attachments, errors = await attachment_service.create_for_room_post(
        attachments_list,
        post_id,
    )

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return [AttachmentListItemSchema.from_orm(attachment) for attachment in attachments]


@room_posts_router.delete(
    '',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def bulk_delete_room_posts(
    room_postDeleteSchema: RoomPostDeleteSchema,
    user: User = Depends(get_current_user),
):
    room_post_service = RoomPostService(user)
    errors = await room_post_service.bulk_delete(
        **room_postDeleteSchema.dict(exclude_unset=True),
    )

    if errors:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=errors)


@room_posts_router.delete(
    '/{post_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id='deleteRoomPost',
)
async def delete_room_post(
    post_id: int,
    user: User = Depends(get_current_user),
):
    room_post_service = RoomPostService(user)
    success, error_messages = await room_post_service.delete(
        id=post_id,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_messages,
        )
