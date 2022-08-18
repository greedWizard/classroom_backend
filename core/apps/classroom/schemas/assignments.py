from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from core.apps.attachments.schemas import AttachmentListItemSchema
from core.apps.users.schemas import AuthorSchema
from core.common.schemas import NormalizedDatetimeModel


class AssignmentRoomNestedSchema(NormalizedDatetimeModel):
    id: int
    name: str

    class Config(NormalizedDatetimeModel.Config):
        orm_mode = True


class AssignmentPostNestedSchema(NormalizedDatetimeModel):
    id: int
    title: str
    room: AssignmentRoomNestedSchema

    class Config(NormalizedDatetimeModel.Config):
        orm_mode = True


class HomeworkAssignmentListitemSchema(NormalizedDatetimeModel):
    id: int
    created_at: datetime
    updated_at: datetime
    author: AuthorSchema
    status: str
    status_assigned: bool
    status_done: bool
    status_request_changes: bool
    comment: Optional[str] = ''
    rate: Optional[int] = None
    post_id: int

    class Config(NormalizedDatetimeModel.Config):
        orm_mode = True


class HomeworkAssignmentDetailSchema(NormalizedDatetimeModel):
    id: int
    created_at: datetime
    updated_at: datetime
    post: AssignmentPostNestedSchema
    author: AuthorSchema
    status: str
    status_assigned: bool
    status_done: bool
    status_request_changes: bool
    comment: Optional[str] = ''
    attachments: Optional[list[AttachmentListItemSchema]] = []
    rate: Optional[int] = None

    class Config(NormalizedDatetimeModel.Config):
        orm_mode = True


class HomeworkAssignmentCreateSuccessSchema(NormalizedDatetimeModel):
    id: int
    created_at: datetime
    updated_at: datetime
    post_id: int
    author_id: int
    status: str
    status_assigned: bool
    status_done: bool
    status_request_changes: bool
    comment: Optional[str] = ''
    rate: Optional[int] = None

    class Config(NormalizedDatetimeModel.Config):
        orm_mode = True


class HomeworkAssignmentCreateSchema(BaseModel):
    post_id: int


class HomeworkAssignmentRequestChangesSchema(BaseModel):
    comment: str


class HomeworkAssignmentRateSchema(BaseModel):
    rate: int
    comment: str = ''
