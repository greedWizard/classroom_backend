from datetime import datetime
from typing import (
    Any,
    Optional,
)

from dependency_injector.wiring import (
    inject,
    Provide,
)
from itsdangerous import TimedSerializer
from pydantic import BaseModel

from apps.common.config import config
from apps.common.containers import MainContainer
from apps.user.schemas import AuthorSchema


def get_current_datetime():
    # TODO: настроить таймзон
    return datetime.utcnow()


# TODO: выпилить
def get_author_data(user) -> BaseModel:
    return AuthorSchema(
        id=user.id,
        first_name=user.first_name,
        last_name=user.last_name,
        middle_name=user.middle_name,
    )


def prepare_json_schema(schema: BaseModel):
    """Workaround to escape the JSONDecode error."""
    base_dict = schema.dict()

    for key in base_dict:
        if isinstance(base_dict[key], datetime):
            base_dict[key] = base_dict[key].isoformat()
    return base_dict


def prepare_json_list(schemas: list[BaseModel]):
    """Workaround to escape the JSONDecode error for list of schemas."""
    return [prepare_json_schema(schema) for schema in schemas]


def get_attachment_path(attachment_id: int) -> str:
    return config.STATIC_URL.format(file_id=attachment_id)


@inject
async def sign_timed_token(
    subject: Any,
    timed_serializer: TimedSerializer = Provide[MainContainer.timed_serializer],
):
    return timed_serializer.dumps(obj=subject, salt=config.PASSWORD_RESET_SALT)


@inject
async def unsign_timed_token(
    token: str,
    salt: Optional[str] = None,
    timed_serializer: TimedSerializer = Provide[MainContainer.timed_serializer],
) -> Any:
    """Method returns value from signed token."""
    return timed_serializer.loads(
        token,
        max_age=config.RESET_PASSWORD_TIMEDELTA.total_seconds(),
        salt=salt,
    )
