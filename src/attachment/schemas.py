from datetime import datetime
from typing import List

from pydantic import BaseModel


class AttachmentCreateSchema(BaseModel):
    filename: str
    source: bytes


class AttachmentListItemSchema(BaseModel):
    id: int
    filename: str
    download_link: str
    type: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class AttachmentDeleteSchema(BaseModel):
    ids: List[int]
