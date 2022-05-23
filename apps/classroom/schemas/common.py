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
