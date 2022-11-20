from io import BytesIO

from PIL import Image


class ImageResizer:
    def get_proportional_size(
        self,
        size_profile_picture: tuple,
        new_size: int,
    ) -> tuple[int, int]:
        aspect_ratio = max(size_profile_picture) / new_size
        size_of_side = int(min(size_profile_picture) / aspect_ratio)

        if max(size_profile_picture) == size_profile_picture[0]:
            return new_size, size_of_side

        return size_of_side, new_size

    def get_resized_picture(self, profile_picture: bytes, new_size: int) -> bytes:
        img = Image.open(BytesIO(profile_picture)).convert('RGB')
        size_profile_picture = img.size

        resized_image = img.resize(
            self.get_proportional_size(size_profile_picture, new_size),
        )
        byte_io = BytesIO()
        resized_image.save(byte_io, format='JPEG')
        return byte_io.getvalue()
