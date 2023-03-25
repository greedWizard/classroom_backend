from pydantic import BaseModel


class TopicCreateSchema(BaseModel):
    title: str
    room_id: int


class TopicUpdateSchema(BaseModel):
    title: str
    order: int


class TopicRetrieveSchema(TopicCreateSchema):
    id: int
    order: int

    class Config:
        orm_mode = True
