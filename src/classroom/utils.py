
from attachment.schemas import AttachmentListItemSchema
from classroom.schemas import HomeworkAssignmentDetailSchema, RoomPostDetailSchema
from user.schemas import AuthorSchema
from .models import HomeworkAssignment, RoomPost


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
    )


async def make_room_post_schema(room_post: RoomPost, assignment: HomeworkAssignment):
    if not room_post:
        return None

    return RoomPostDetailSchema(
        title=room_post.title,
        room=room_post.room,
        description=room_post.description,
        id=room_post.id,
        text=room_post.text,
        author=AuthorSchema.from_orm(room_post.author),
        attachments=await room_post.attachments,
        created_at=room_post.created_at,
        updated_at=room_post.updated_at,
        attachments_count=room_post.attachments_count,
        type=room_post.type,
        assignment=await make_homework_assignment_schema(
            assignment=assignment
        ),
    ) 
