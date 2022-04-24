from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from attachment.schemas import AttachmentListItemSchema
from core.schemas import NormalizedDatetimeModel
from user.schemas import AuthorSchema


class RoomBaseSchema(NormalizedDatetimeModel):
    name: str
    description: Optional[str]

    class Config:
        orm_mode = True


class RoomCreateSchema(RoomBaseSchema):
    pass


class RoomPostAbstractSchema(BaseModel):
    title: str
    description: Optional[str]


class RoomCreateSuccessSchema(RoomCreateSchema):
    id: int


class RoomParticipationSchema(BaseModel):
    id: int
    role: str
    user_id: int
    room_id: int
    created_at: datetime


class RoomDetailSchema(RoomBaseSchema, NormalizedDatetimeModel):
    id: int
    name: str
    description: Optional[str]
    participations_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    author: AuthorSchema


class RoomListItemSchema(RoomBaseSchema, NormalizedDatetimeModel):
    id: int
    participations_count: int = 0
    participation: Optional[RoomParticipationSchema]
    created_at: datetime

    class Config:
        orm_mode = True


class RoomCreateJoinLinkSuccessSchema(BaseModel):
    join_slug: str


class ParticipationCreateSchema(BaseModel):
    user_id: int
    room_id: int
    role: Optional[str]
    author_id: int


class ParticipationCreateByJoinSlugSchema(BaseModel):
    user_id: int
    join_slug: str
    role: Optional[str]
    author_id: int


class UserParticipationSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    middle_name: Optional[str]


class ParticipationListItemSchema:
    user: UserParticipationSchema
    room: RoomListItemSchema
    created_at: datetime


class ParticipationSuccessSchema(BaseModel):
    id: int
    user_id: int
    role: Optional[str]
    author_id: int
    room: RoomListItemSchema


class RoomDeleteSchema(BaseModel):
    id: int


class MaterialCreateSchema(RoomPostAbstractSchema):
    room_id: int
    text: Optional[str]
    author_id: Optional[int]


class MaterialCreateSuccessSchema(MaterialCreateSchema):
    id: int


class MaterialListItemSchema(RoomPostAbstractSchema):
    id: int
    text: Optional[str]
    author: AuthorSchema
    created_at: datetime
    updated_at: datetime
    room_id: int

    class Config:
        orm_mode = True


class MaterialUpdateSchema(MaterialCreateSchema):
    pass


class MaterialDetailSchema(MaterialListItemSchema):
    attachments: List[AttachmentListItemSchema]
    room_id: int

    class Config:
        orm_mode = True


class MaterialDeleteSchema(BaseModel):
    ids: List[int]
