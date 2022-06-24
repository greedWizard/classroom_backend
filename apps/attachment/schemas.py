from datetime import datetime
from typing import List

from pydantic import BaseModel

from apps.common.schemas import NormalizedDatetimeModel


class AttachmentCreateSchema(BaseModel):
    filename: str
    source: bytes


class AttachmentListItemSchema(NormalizedDatetimeModel):
    id: int
    filename: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class AttachmentDeleteSchema(BaseModel):
    ids: List[int]
