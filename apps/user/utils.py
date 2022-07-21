import hashlib
from typing import (
    Any,
    Optional,
)
from PIL import Image
from io import BytesIO
from dependency_injector.wiring import (
    inject,
    Provide,
)
from itsdangerous import TimedSerializer

from apps.common.config import config
from apps.common.containers import MainContainer


def hash_string(string: str):
    return hashlib.md5(string.encode()).hexdigest()


def get_the_length_of_the_sides(profile_photo_size: tuple[int, int]) -> tuple[int, int]:
    fixed_size = config.PROFILE_PHOTO_RESOLUTION
    aspect_ratio = max(profile_photo_size) / fixed_size
    size_of_side = int(min(profile_photo_size) / aspect_ratio)

    if max(profile_photo_size) == profile_photo_size[0]:
        return fixed_size, size_of_side
    else:
        return size_of_side, fixed_size


def resize_profile_photo(img, profile_photo_size: tuple[int, int]):
    new_image = img.resize((get_the_length_of_the_sides(profile_photo_size)))
    byte_io = BytesIO()
    new_image.save(byte_io, format='JPEG')
    return byte_io.getvalue()


def get_bytes_of_profile_photo(profile_photo):
    img = Image.open(profile_photo)
    size_profile_photo = img.size
    return resize_profile_photo(img, size_profile_photo)


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
