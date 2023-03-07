from pydantic import BaseModel


class VKResponseAccessDataSchema(BaseModel):
    access_token: str
    user_id: str
    email: str = ''


class VKResponseUserInfoSchema(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    photo_400_orig: str = ''
