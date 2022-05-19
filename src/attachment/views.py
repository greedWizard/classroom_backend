from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import StreamingResponse

from starlette import status
from attachment.schemas import AttachmentDeleteSchema

from attachment.services.attachment_service import AttachmentService
from attachment.utils import stream_file

from user.models import User
from user.dependencies import get_current_user


router = APIRouter(
    tags=['attachments']
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
            'Content-Disposition': f'attachment; filename='
        }
    )


@router.delete(
    '',
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id='deleteAttachments',
)
async def delete_attachments(
    attachmentDeleteSchema: AttachmentDeleteSchema,
    user: User = Depends(get_current_user),
):
    attachment_service = AttachmentService(user)
    errors = await attachment_service.bulk_delete(id__in=attachmentDeleteSchema.ids)

    if errors:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=errors)


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
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=error_messages)
