import hashlib
from io import BytesIO

from core.common.containers import MainContainer
from core.common.helpers.image_resizer import ImageResizer
from dependency_injector.wiring import (
    inject,
    Provide,
)


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
