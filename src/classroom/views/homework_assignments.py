from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter

from starlette import status

from classroom.schemas import HomeworkAssignmentDetailSchema, HomeworkAssignmentMarkAsDoneSchema, HomeworkAssignmentRequestChangesSchema, HomeworkAssignmentCreateSchema, HomeworkAssignmentCreateSuccessSchema
from classroom.services.homework_assignment_service import HomeworkAssignmentService
from user.dependencies import get_current_user
from user.models import User



router = APIRouter()


@router.post(
    '',
    response_model=HomeworkAssignmentCreateSuccessSchema,
    operation_id='assignHomework',
    status_code=status.HTTP_201_CREATED,
)
async def assign_homework(
    create_schema: HomeworkAssignmentCreateSchema,
    user: User = Depends(get_current_user)
):
    service = HomeworkAssignmentService(user)

    homework_assignment, errors = await service.create(create_schema)

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return HomeworkAssignmentCreateSuccessSchema.from_orm(homework_assignment)


@router.post(
    '/{assignment_id}/request-changes',
    response_model=HomeworkAssignmentDetailSchema,
    operation_id='requestAssignmentChanges',
    status_code=status.HTTP_200_OK,
)
async def request_homework_assignment_changes(
    assignment_id: int,
    changes_schema: HomeworkAssignmentRequestChangesSchema,
    user: User = Depends(get_current_user)
):
    service = HomeworkAssignmentService(user)

    homework_assignment, errors = await service.request_changes(
        assignment_id=assignment_id,
        changes_schema=changes_schema,
    )

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return HomeworkAssignmentDetailSchema.from_orm(homework_assignment)


@router.get(
    '/by-room-post/{assigned_room_post_id}',
    response_model=list[HomeworkAssignmentDetailSchema],
    operation_id='getAssignmentsForTeacher',
    status_code=status.HTTP_200_OK,
)
async def fetch_assignments_for_teacher(
    assigned_room_post_id: int,
    user: User = Depends(get_current_user)
):
    service = HomeworkAssignmentService(user)

    homework_assignments, _ = await service.fetch_for_teacher(
        assigned_room_post_id=assigned_room_post_id,
    )
    return [HomeworkAssignmentDetailSchema.from_orm(assignment) \
                            for assignment in homework_assignments]


@router.post(
    '/{assignment_id}/mark-done',
    response_model=HomeworkAssignmentDetailSchema,
    operation_id='markAssignmentAsDone',
    status_code=status.HTTP_200_OK,
)
async def mark_assignment_as_done(
    assignment_id: int,
    changes_schema: HomeworkAssignmentMarkAsDoneSchema,
    user: User = Depends(get_current_user)
):
    service = HomeworkAssignmentService(user)

    homework_assignment, errors = await service.mark_as_done(
        assignment_id=assignment_id,
        changes_schema=changes_schema,
    )

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return HomeworkAssignmentDetailSchema.from_orm(homework_assignment)

