from typing import Optional

from starlette import status

from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
)
from fastapi.exceptions import HTTPException
from fastapi.responses import StreamingResponse

from apps.attachment.schemas import (
    AttachmentBulkCreateResponse,
    AttachmentCreateSchema,
)
from apps.attachment.services.attachment_service import AttachmentService
from apps.attachment.utils import stream_file
from apps.user.dependencies import get_current_user
from apps.user.models import User


router = APIRouter(
    tags=['attachments'],
)


@router.get(
    '/{attachment_id}',
    status_code=status.HTTP_206_PARTIAL_CONTENT,
    operation_id='getAttachment',
)
async def get_attachment(
    attachment_id: int,
    user: User = Depends(get_current_user),
):
    attachment_service = AttachmentService(user)
    attachment, errors = await attachment_service.retrieve(id=attachment_id)

    if errors:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=errors)
    return StreamingResponse(
        content=stream_file(attachment.source),
        headers={
            'Content-Disposition': f'attachment; filename=',
        },
    )


@router.post(
    '/',
    response_model=AttachmentBulkCreateResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id='createAttachments',
)
async def create_attachments(
    attachments: list[UploadFile],
    post_id: Optional[int] = None,
    assignment_id: Optional[int] = None,
    user: User = Depends(get_current_user),
):
    if all([post_id is None, assignment_id is None]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={'error': 'Either post_id or room_id must be provided!'},
        )

    attachments_list = [
        AttachmentCreateSchema(
            filename=attachment.filename,
            source=await attachment.read(),
            assignment_id=assignment_id,
            post_id=post_id,
        )
        for attachment in attachments
    ]

    attachment_service = AttachmentService(user)
    attachments, errors = await attachment_service.bulk_create(
        attachments_list,
    )

    if not attachments:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return AttachmentBulkCreateResponse(created=attachments, errors=errors)


@router.delete(
    '/{attachment_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id='deleteAttachment',
)
async def delete_attachment(
    attachment_id: int,
    user: User = Depends(get_current_user),
):
    attachment_service = AttachmentService(user)
    success, error_messages = await attachment_service.delete_by_id(id=attachment_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_messages,
        )
