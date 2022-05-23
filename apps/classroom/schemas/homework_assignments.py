from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from apps.attachment.schemas import AttachmentListItemSchema
from apps.user.schemas import AuthorSchema
from common.schemas import NormalizedDatetimeModel


class HomeworkAssignmentDetailSchema(NormalizedDatetimeModel):
    id: int
    created_at: datetime
    updated_at: datetime
    assigned_room_post_id: int
    author: AuthorSchema
    status: str
    comment: Optional[str] = ''
    attachments: Optional[list[AttachmentListItemSchema]] = []
    rate: Optional[int] = None

    class Config(NormalizedDatetimeModel.Config):
        orm_mode = True


class HomeworkAssignmentCreateSchema(BaseModel):
    assigned_room_post_id: int


class HomeworkAssignmentRequestChangesSchema(BaseModel):
    comment: str


class HomeworkAssignmentRateSchema(BaseModel):
    rate: int
    comment: str = ''


class HomeworkAssignmentCreateSuccessSchema(NormalizedDatetimeModel):
    id: int
    created_at: datetime
    author_id: int

    class Config(NormalizedDatetimeModel.Config):
        orm_mode = True
