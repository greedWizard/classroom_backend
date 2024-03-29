from typing import Union

from core.apps.attachments.models import Attachment
from core.apps.classroom.models import (
    HomeworkAssignment,
    RoomPost,
)


def check_attachment_is_attached(
    attachment: Attachment,
    attached_to: Union[RoomPost, HomeworkAssignment],
    file_path: str,
):
    with open(file_path, 'rb') as upload_file:
        file_content = upload_file.read()

    assert attachment
    assert attachment.source == file_content
    assert attachment.id in [
        assignment_attachment.id for assignment_attachment in attached_to.attachments
    ]
