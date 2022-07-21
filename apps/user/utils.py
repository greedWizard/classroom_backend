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


class ImageResize:
    def __init__(self, profile_picture: bytes):
        self.img = Image.open(BytesIO(profile_picture))
        self.size_profile_picture = self.img.size

    def get_the_length_of_the_sides(self, new_size: int) -> tuple[int, int]:
        aspect_ratio = max(self.size_profile_picture) / new_size
        size_of_side = int(min(self.size_profile_picture) / aspect_ratio)

        if max(self.size_profile_picture) == self.size_profile_picture[0]:
            return new_size, size_of_side

        return size_of_side, new_size

    def get_resized_picture(self, new_size: int) -> bytes:
        new_image = self.img.resize((self.get_the_length_of_the_sides(new_size)))
        byte_io = BytesIO()
        new_image.save(byte_io, format='JPEG')
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
