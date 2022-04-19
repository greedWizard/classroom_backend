from typing import List, TypedDict

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from starlette import status
from attachment.schemas import AttachmentCreateSchema, AttachmentDeleteSchema, AttachmentListItemSchema

from attachment.services.attachment_service import AttachmentService

from core.config import config
from core.utils import get_author_data

from user.models import User
from user.utils import get_current_user


router = APIRouter(
    tags=['attachments']
)


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
