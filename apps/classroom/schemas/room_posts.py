from datetime import datetime
from typing import (
    List,
    Optional,
)

from pydantic import BaseModel

from apps.attachment.schemas import AttachmentListItemSchema
from apps.common.schemas import NormalizedDatetimeModel
from apps.user.schemas import AuthorSchema


class RoomBaseSchema(NormalizedDatetimeModel):
    name: str
    description: Optional[str]

    class Config:
        orm_mode = True


class RoomNestedSchema(RoomBaseSchema, NormalizedDatetimeModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        orm_mode = True


class RoomPostAbstractSchema(BaseModel):
    title: str
    description: Optional[str]
    type: str

    class Config:
        orm_mode = True


class RoomPostCreateSchema(RoomPostAbstractSchema):
    room_id: int
    text: Optional[str]
    author_id: Optional[int]
    type: str


class RoomPostCreateSuccessSchema(RoomPostCreateSchema):
    id: int


class RoomPostUpdateSchema(BaseModel):
    type: str
    description: Optional[str] = None
    text: Optional[str] = None
    title: str


class RoomPostDetailSchema(BaseModel):
    id: int
    text: Optional[str]
    title: str
    description: Optional[str]
    type: str
    author: AuthorSchema
    created_at: datetime
    updated_at: datetime
    attachments_count: int
    attachments: List[AttachmentListItemSchema]
    room: RoomNestedSchema

    class Config:
        orm_mode = True


class RoomPostEmailNotificationSchema(BaseModel):
    id: int
    title: str
    room: RoomNestedSchema
    author: AuthorSchema
    type: str
    subject_link: Optional[str] = None

    class Config:
        orm_mode = True


class RoomPostDeleteSchema(BaseModel):
    ids: List[int]
