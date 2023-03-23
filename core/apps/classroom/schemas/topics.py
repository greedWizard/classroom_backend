from pydantic import BaseModel


class TopicCreateSchema(BaseModel):
    title: str
    order: int = 0
    room_id: int


class TopicUpdateSchema(BaseModel):
    title: str
    order: int


class RetrieveTopicSchema(TopicCreateSchema):
    id: int
