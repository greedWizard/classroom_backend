from io import TextIOWrapper
from typing import Union

from apps.attachment.models import Attachment
from apps.classroom.models import RoomPost, HomeworkAssignment


def check_attachment_is_attached(
    attachment: Attachment,
    attached_to: Union[RoomPost, HomeworkAssignment],
    file_path: str,
):
    with open(file_path, 'rb') as upload_file:
        file_content = upload_file.read()

    assert attachment
    assert attachment.source == file_content
    assert attachment.id in \
        [assignment_attachment.id for assignment_attachment in attached_to.attachments]
