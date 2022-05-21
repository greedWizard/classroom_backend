from pydantic import BaseModel

from user.models import User
from user.schemas import AuthorSchema


def get_author_data(user: User) -> BaseModel:
    return AuthorSchema(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        middle_name=user.middle_name,
    )
