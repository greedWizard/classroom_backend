from datetime import datetime

from pydantic import BaseModel

from core.apps.users.schemas import AuthorSchema


class MessageSchema(BaseModel):
    id: int
    sender: AuthorSchema
    reciever: AuthorSchema
    created_at: datetime
    text: str

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }


class MessageCreateSchema(BaseModel):
    sender_id: int
    text: str
    dialog_id: int


class MessageDetailSchema(BaseModel):
    sender: AuthorSchema
    text: str
    is_read: bool
    dialog_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class DialogNestedSchema(BaseModel):
    id: int
    sender: AuthorSchema
    reciever: AuthorSchema
    created_at: datetime

    class Config:
        orm_mode = True


class DialogCreateSchema(BaseModel):
    author_id: int
    updated_by_id: int


class DialogDetailSchema(BaseModel):
    id: int
    participants: list[AuthorSchema]
    author: AuthorSchema
    created_at: datetime

    class Config:
        orm_mode = True


class DialogStartSchema(BaseModel):
    participants_ids: list[int]


class MessageListItemSchema(BaseModel):
    id: int
    sender: AuthorSchema
    reciever: AuthorSchema
    text: str
    created_at: datetime
    dialog: DialogNestedSchema

    class Config:
        orm_mode = True

class DialogWithParticipantsSchema(BaseModel):
    id: int
    participants: list[AuthorSchema]
    participants_count: int

    class Config:
        orm_mode = True


class LastMessageDetail(BaseModel):
    id: int
    sender: AuthorSchema
    text: str
    is_read: bool
    dialog: DialogWithParticipantsSchema
    created_at: datetime

    class Config:
        orm_mode = True

