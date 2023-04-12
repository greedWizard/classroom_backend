from typing import Optional

from pydantic import BaseModel


class TopicCreateSchema(BaseModel):
    title: str
    room_id: int


class TopicUpdateSchema(BaseModel):
    title: Optional[str] = None
    order: Optional[int] = None


class TopicRetrieveSchema(TopicCreateSchema):
    id: int
    order: int

    class Config:
        orm_mode = True
