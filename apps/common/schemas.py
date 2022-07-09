from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NormalizedDatetimeModel(BaseModel):
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.strftime('%d, %h %Y %H:%M'),
        }


class OperationResultSchema(BaseModel):
    status: str
    message: Optional[str] = None
