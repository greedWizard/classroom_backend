from pydantic import BaseModel


class ChangeLocalizationSchema(BaseModel):
    language_code: str
