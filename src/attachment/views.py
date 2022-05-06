from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.responses import StreamingResponse

from starlette import status
from attachment.schemas import AttachmentDeleteSchema

from attachment.services.attachment_service import AttachmentService

from user.models import User
from user.utils import get_current_user


router = APIRouter(
    tags=['attachments']
)


@router.get(
    '',
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
    return StreamingResponse(await attachment.stream())


@router.delete(
    '',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_attachments(
    attachmentDeleteSchema: AttachmentDeleteSchema,
    user: User = Depends(get_current_user),
):
    attachment_service = AttachmentService(user)
    errors = await attachment_service.bulk_delete(id__in=attachmentDeleteSchema.ids)

    if errors:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=errors)
