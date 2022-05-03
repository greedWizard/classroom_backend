from datetime import datetime
from typing import List

from pydantic import BaseModel

from core.schemas import NormalizedDatetimeModel


class AttachmentCreateSchema(BaseModel):
    filename: str
    source: bytes


class AttachmentListItemSchema(NormalizedDatetimeModel):
    id: int
    filename: str
    download_link: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class AttachmentDeleteSchema(BaseModel):
    ids: List[int]
