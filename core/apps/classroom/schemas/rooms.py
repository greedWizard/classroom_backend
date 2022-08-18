from datetime import datetime
from typing import Optional

from core.apps.classroom.schemas.common import RoomBaseSchema
from core.apps.users.schemas import AuthorSchema
from core.common.schemas import NormalizedDatetimeModel
from pydantic import BaseModel


class RoomCreateSchema(RoomBaseSchema):
    pass


class RoomCreateSuccessSchema(RoomCreateSchema):
    id: int


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
    created_at: datetime
    author: AuthorSchema

    class Config:
        orm_mode = True


class RoomNestedSchema(RoomBaseSchema, NormalizedDatetimeModel):
    id: int
    name: str
    created_at: datetime
    author: AuthorSchema

    class Config:
        orm_mode = True


class RoomCreateJoinLinkSuccessSchema(BaseModel):
    join_slug: str


class RoomDeleteSchema(BaseModel):
    id: int
