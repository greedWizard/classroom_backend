from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from common.schemas import NormalizedDatetimeModel


class AuthorSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    middle_name: Optional[str] = None

    class Config:
        orm_mode = True


class UserRegisterSchema(BaseModel):
    first_name: str
    last_name: str
    password: str
    repeat_password: str
    phone_number: str
    email: str
    middle_name: Optional[str] = None
    accept_eula: bool = False


class UserRegistrationCompleteSchema(BaseModel):
    status: str
    is_active: bool = False


class UserLoginSchema(BaseModel):
    email: str = None
    phone_number: str = None
    password: str


class UserLoginSuccessSchema(BaseModel):
    access_token: str
    refresh_token: str


class UserProfileSchema(NormalizedDatetimeModel):
    id: int
    email: str
    phone_number: str
    first_name: str
    last_name: str
    middle_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        orm_mode = True


class UserProfileUpdateSchema(BaseModel):
    password: Optional[str]
    repeat_password: Optional[str]
    confirm_password: str
    email: Optional[str]
    phone_number: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    middle_name: Optional[str]


class UserActivationEmailSchema(BaseModel):
    email: str
    activation_link: str
