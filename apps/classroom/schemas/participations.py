from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from common.schemas import NormalizedDatetimeModel


class ParticipationNestedSchema(BaseModel):
    id: int
    role: str
    user_id: int
    room_id: int
    created_at: datetime


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
    email: str
    middle_name: Optional[str]


class ParticipationListItemSchema(NormalizedDatetimeModel):
    id: int
    user: ParticipationUserSchema
    role: str
    created_at: datetime

    class Config:
        orm_mode = True


class ParticipationDetailSchema(NormalizedDatetimeModel):
    id: int
    role: str
    created_at: datetime
    can_manage_posts: bool
    can_examine: bool
    can_assign_homeworks: bool
    room_id: int

    class Config:
        orm_mode = True


class ParticipationSuccessSchema(BaseModel):
    id: int
    user_id: int
    role: Optional[str]
    author_id: int
