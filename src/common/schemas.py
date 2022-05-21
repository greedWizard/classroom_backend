from datetime import datetime
from pydantic import BaseModel


class NormalizedDatetimeModel(BaseModel):
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.strftime('%d, %h %Y %H:%M')
        }
