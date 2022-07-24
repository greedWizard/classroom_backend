import hashlib
from io import BytesIO
from typing import (
    Any,
    Optional,
)

from dependency_injector.wiring import (
    inject,
    Provide,
)
from itsdangerous import TimedSerializer

from apps.common.config import config
from apps.common.containers import MainContainer
from apps.common.helpers.image_resizer import ImageResizer


def hash_string(string: str):
    return hashlib.md5(string.encode()).hexdigest()


@inject
async def resize_image(
    picture_bytes: BytesIO,
    new_size: int,
    image_resizer: ImageResizer = Provide[MainContainer.image_resizer],
) -> BytesIO:
    return image_resizer.get_resized_picture(
        picture_bytes,
        new_size=new_size,
    )


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
