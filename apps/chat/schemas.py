from datetime import datetime

from pydantic import BaseModel

from apps.user.schemas import AuthorSchema


class DialogCreateSchema(BaseModel):
    sender_id: int
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
    sender_id: int
    reciever_id: int
    text: str
    dialog_id: int
