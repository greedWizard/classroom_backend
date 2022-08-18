from datetime import datetime

from core.apps.users.schemas import AuthorSchema
from pydantic import BaseModel


class DialogCreateSchema(BaseModel):
    reciever_id: int


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
    reciever_id: int
    text: str
    dialog_id: int


class DialogNestedSchema(BaseModel):
    id: int
    sender: AuthorSchema
    reciever: AuthorSchema
    created_at: datetime

    class Config:
        orm_mode = True


class MessageListItemSchema(BaseModel):
    id: int
    sender: AuthorSchema
    reciever: AuthorSchema
    text: str
    created_at: datetime
    dialog: DialogNestedSchema

    class Config:
        orm_mode = True
