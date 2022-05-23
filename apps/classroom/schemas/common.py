from datetime import datetime
from typing import Optional

from apps.user.schemas import AuthorSchema
from common.schemas import NormalizedDatetimeModel


class RoomBaseSchema(NormalizedDatetimeModel):
    name: str
    description: Optional[str]

    class Config:
        orm_mode = True


class RoomNestedSchema(RoomBaseSchema, NormalizedDatetimeModel):
    id: int
    name: str
    created_at: datetime
    author: AuthorSchema

    class Config:
        orm_mode = True


class RoomPostListItemSchema(NormalizedDatetimeModel):
    id: int
    text: Optional[str]
    author: AuthorSchema
    created_at: datetime
    updated_at: datetime
    attachments_count: int
    room_id: int
    type: str

    class Config(NormalizedDatetimeModel.Config):
        orm_mode = True
