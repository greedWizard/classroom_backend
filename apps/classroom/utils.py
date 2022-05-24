from apps.classroom.schemas import HomeworkAssignmentDetailSchema, RoomPostDetailSchema
from apps.classroom.schemas.common import RoomNestedSchema, RoomPostListItemSchema
from apps.classroom.schemas.rooms import RoomDetailSchema
from apps.user.schemas import AuthorSchema

from .models import HomeworkAssignment, Room, RoomPost


async def make_homework_assignment_schema(assignment: HomeworkAssignment):
    if not assignment:
        return None

    return HomeworkAssignmentDetailSchema(
        id=assignment.id,
        created_at=assignment.created_at,
        updated_at=assignment.updated_at,
        assigned_room_post_id=assignment.assigned_room_post_id,
        author=assignment.author,
        attachments=await assignment.attachments,
        status=assignment.status,
        comment=assignment.comment,
        rate=assignment.rate,
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


async def make_room_detail_schema(
    room: Room,
):
    if not room:
        return None

    return RoomDetailSchema(
        name=room.name,
        description=room.description,
        id=room.id,
        participations_count=room.participations_count,
        created_at=room.created_at,
        updated_at=room.updated_at,
        author=AuthorSchema.from_orm(room.author),
        join_slug=room.join_slug,
        room_posts=[
            RoomPostListItemSchema.from_orm(room_post) for room_post in room.room_posts
        ],
    )
