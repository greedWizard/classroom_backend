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


class ImageResizer:

    def get_the_length_of_the_sides(self, size_profile_picture: tuple, new_size: int) -> tuple[int, int]:
        aspect_ratio = max(size_profile_picture) / new_size
        size_of_side = int(min(size_profile_picture) / aspect_ratio)

        if max(size_profile_picture) == size_profile_picture[0]:
            return new_size, size_of_side

        return size_of_side, new_size

    def get_resized_picture(self, profile_picture: bytes, new_size: int) -> bytes:
        img = Image.open(BytesIO(profile_picture))
        size_profile_picture = img.size

        resized_image = img.resize(
            (self.get_the_length_of_the_sides(size_profile_picture, new_size))
        )
        byte_io = BytesIO()
        resized_image.save(byte_io, format='JPEG')
        return byte_io.getvalue()


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
