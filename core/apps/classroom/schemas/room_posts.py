from datetime import datetime
from typing import (
    List,
    Optional,
)

from pydantic import BaseModel

from core.apps.attachments.schemas import AttachmentListItemSchema
from core.apps.classroom.constants import RoomPostType
from core.apps.users.schemas import AuthorSchema
from core.common.schemas import NormalizedDatetimeModel


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
    type: RoomPostType
    text: Optional[str]
    topic_id: Optional[int] = None


class RoomPostCreateSuccessSchema(RoomPostCreateSchema):
    id: int


class RoomPostUpdateSchema(BaseModel):
    type: Optional[str] = None
    description: Optional[str] = None
    text: Optional[str] = None
    title: Optional[str] = None
    topic_id: Optional[int] = None


class RoomPostDetailSchema(BaseModel):
    id: int
    text: Optional[str]
    title: str
    description: Optional[str]
    type: str
    author_id: int
    created_at: datetime
    updated_at: datetime
    attachments_count: int
    assignments_count: int
    attachments: List[AttachmentListItemSchema]
    room_id: int
    is_assignable: bool

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
