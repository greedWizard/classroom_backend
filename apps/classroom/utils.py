from apps.classroom.schemas import (
    HomeworkAssignmentDetailSchema,
    RoomPostDetailSchema,
)
from apps.classroom.schemas.common import RoomNestedSchema
from apps.user.schemas import AuthorSchema

from .models import (
    HomeworkAssignment,
    RoomPost,
)




async def make_room_post_schema(room_post: RoomPost):
    if not room_post:
        return None

    return RoomPostDetailSchema(
        title=room_post.title,
        room=RoomNestedSchema.from_orm(room_post.room),
        description=room_post.description,
        id=room_post.id,
        text=room_post.text,
        author=AuthorSchema.from_orm(room_post.author),
        attachments=await room_post.attachments,
        created_at=room_post.created_at,
        updated_at=room_post.updated_at,
        attachments_count=room_post.attachments_count,
        type=room_post.type,
    )
