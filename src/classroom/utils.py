
from classroom.schemas import HomeworkAssignmentDetailSchema
from .models import HomeworkAssignment


async def make_homework_assignment_schema(assignment: HomeworkAssignment):
    return HomeworkAssignmentDetailSchema(
        id=assignment.id,
        created_at=assignment.created_at,
        updated_at=assignment.updated_at,
        assigned_room_post_id=assignment.assigned_room_post_id,
        author=assignment.author,
        attachments=await assignment.attachments,
    )
