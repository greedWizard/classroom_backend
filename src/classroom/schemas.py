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
    type: str

    class Config:
        orm_mode = True


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
    join_slug: str


class RoomListItemSchema(RoomBaseSchema, NormalizedDatetimeModel):
    id: int
    participations_count: int = 0
    participation: Optional[RoomParticipationSchema]
    created_at: datetime
    author: AuthorSchema

    class Config:
        orm_mode = True


class RoomNestedSchema(RoomBaseSchema, NormalizedDatetimeModel):
    id: int
    created_at: datetime
    author: AuthorSchema

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


class ParticipationUserSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    middle_name: Optional[str]


class ParticipationListItemSchema(NormalizedDatetimeModel):
    id: int
    user: ParticipationUserSchema
    room: RoomCreateSuccessSchema
    role: str
    created_at: datetime

    class Config:
        orm_mode = True


class ParticipationSuccessSchema(BaseModel):
    id: int
    user_id: int
    role: Optional[str]
    author_id: int
    room: RoomListItemSchema


class RoomDeleteSchema(BaseModel):
    id: int


class RoomPostCreateSchema(RoomPostAbstractSchema):
    room_id: int
    text: Optional[str]
    author_id: Optional[int]
    type: str


class RoomPostCreateSuccessSchema(RoomPostCreateSchema):
    id: int


class RoomPostListItemSchema(RoomPostAbstractSchema, NormalizedDatetimeModel):
    id: int
    text: Optional[str]
    author: AuthorSchema
    created_at: datetime
    updated_at: datetime
    attachments_count: int
    room_id: int

    class Config(NormalizedDatetimeModel.Config):
        orm_mode = True


class RoomPostUpdateSchema(BaseModel):
    type: str
    description: Optional[str] = None
    text: Optional[str] = None
    title: str


class HomeworkAssignmentDetailSchema(NormalizedDatetimeModel):
    id: int
    created_at: datetime
    updated_at: datetime
    assigned_room_post_id: int
    author: AuthorSchema
    comment: Optional[str] = ''
    attachments: Optional[list[AttachmentListItemSchema]] = []

    class Config(NormalizedDatetimeModel.Config):
        orm_mode = True


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
    assignment: Optional[HomeworkAssignmentDetailSchema] = None

    class Config:
        orm_mode = True


class RoomPostDeleteSchema(BaseModel):
    ids: List[int]


class HomeworkAssignmentCreateSchema(BaseModel):
    assigned_room_post_id: int


class HomeworkAssignmentRequestChangesSchema(BaseModel):
    comment: str


class HomeworkAssignmentMarkAsDoneSchema(BaseModel):
    rate: int
    comment: str = ''


class HomeworkAssignmentCreateSuccessSchema(NormalizedDatetimeModel):
    id: int
    created_at: datetime
    author_id: int

    class Config(NormalizedDatetimeModel.Config):
        orm_mode = True
