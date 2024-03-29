from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from core.apps.classroom.schemas.rooms import RoomDetailSchema
from core.common.schemas import NormalizedDatetimeModel


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
    profile_picture_path: Optional[str] = None

    class Config:
        orm_mode = True


class ParticipationListItemSchema(NormalizedDatetimeModel):
    id: int
    user: ParticipationUserSchema
    role: str
    created_at: datetime
    room_id: int

    class Config:
        orm_mode = True


class ParticipationCurrentUserSchema(NormalizedDatetimeModel):
    id: int
    role: str
    created_at: datetime
    can_manage_posts: bool
    can_examine: bool
    can_assign_homeworks: bool
    can_remove_participants: bool
    can_manage_assignments: bool
    is_moderator: bool
    can_create_topics: bool
    room_id: int

    class Config:
        orm_mode = True


class ParticipationDetailSchema(NormalizedDatetimeModel):
    id: int
    role: str
    created_at: datetime
    can_manage_posts: bool
    can_examine: bool
    can_assign_homeworks: bool
    can_remove_participants: bool
    can_manage_assignments: bool
    is_moderator: bool
    can_create_topics: bool
    room: RoomDetailSchema

    class Config:
        orm_mode = True


class ParticipationSuccessSchema(BaseModel):
    id: int
    user_id: int
    role: Optional[str]
    author_id: int

    class Config:
        orm_mode = True
