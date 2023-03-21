from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from core.common.config import config
from core.common.schemas import NormalizedDatetimeModel


class AuthorSchema(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str = ''
    middle_name: Optional[str] = None
    profile_picture_path: Optional[str] = None
    full_name: str

    class Config:
        orm_mode = True


class UserRegisterSchema(BaseModel):
    first_name: str
    last_name: str
    password: str
    repeat_password: str
    email: str
    middle_name: Optional[str] = None
    accept_eula: bool = False


class UserRegistrationCompleteSchema(BaseModel):
    status: str = config.USER_SUCCESS_STATUS
    is_active: bool = False
    email: str

    class Config:
        orm_mode = True


class UserLoginSchema(BaseModel):
    email: str = None
    password: str


class UserLoginSuccessSchema(BaseModel):
    access_token: str
    token_type: str


class UserProfileSchema(NormalizedDatetimeModel):
    id: int
    email: Optional[str]
    first_name: str
    last_name: str
    middle_name: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool
    profile_picture_path: Optional[str]

    class Config:
        orm_mode = True


class UserProfileUpdateSchema(BaseModel):
    password: Optional[str]
    repeat_password: Optional[str]
    confirm_password: str
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    middle_name: Optional[str]


class UserHyperlinkEmailSchema(BaseModel):
    email: str
    hyperlink: str
    first_name: str = ''


class UserPasswordResetInitiationSchema(BaseModel):
    email: str


class UserPasswordResetSchema(BaseModel):
    password: str
    repeat_password: str


class ProfilePicturePath(BaseModel):
    profile_picture_path: Optional[str] = None

    class Config:
        orm_mode = True
