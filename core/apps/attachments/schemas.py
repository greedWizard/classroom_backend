from datetime import datetime
from typing import (
    List,
    Optional,
)

from core.common.schemas import NormalizedDatetimeModel
from pydantic import BaseModel


class AttachmentCreateSchema(BaseModel):
    filename: str
    source: bytes
    post_id: Optional[int] = None
    assignment_id: Optional[int] = None

    class Config:
        orm_mode = True


class AttachmentCreateSuccessSchema(BaseModel):
    id: int
    filename: str
    post_id: Optional[int] = None
    assignment_id: Optional[int] = None

    class Config:
        orm_mode = True


class AttachmentError(BaseModel):
    room_id: Optional[str] = None
    assignment_id: Optional[str] = None
    post_id: Optional[str] = None


class AttachmentBulkCreateResponse(BaseModel):
    created: Optional[list[AttachmentCreateSuccessSchema]] = None
    errors: Optional[list[AttachmentError]] = None


class AttachmentListItemSchema(NormalizedDatetimeModel):
    id: int
    filename: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class AttachmentDeleteSchema(BaseModel):
    ids: List[int]
