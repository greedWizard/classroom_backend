from starlette import status

from fastapi import (
    Depends,
    UploadFile,
)
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter

from apps.attachment.schemas import (
    AttachmentCreateSchema,
    AttachmentListItemSchema,
)
from apps.attachment.services.attachment_service import AttachmentService
from apps.classroom.schemas import (
    HomeworkAssignmentCreateSchema,
    HomeworkAssignmentCreateSuccessSchema,
    HomeworkAssignmentDetailSchema,
    HomeworkAssignmentRateSchema,
    HomeworkAssignmentRequestChangesSchema,
)
from apps.classroom.services.homework_assignment_service import (
    HomeworkAssignmentService,
)
from apps.classroom.utils import make_homework_assignment_schema
from apps.user.dependencies import get_current_user
from apps.user.models import User


router = APIRouter()


@router.post(
    '',
    response_model=HomeworkAssignmentCreateSuccessSchema,
    operation_id='assignHomework',
    status_code=status.HTTP_201_CREATED,
)
async def assign_homework(
    create_schema: HomeworkAssignmentCreateSchema,
    user: User = Depends(get_current_user),
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
    user: User = Depends(get_current_user),
):
    service = HomeworkAssignmentService(user)

    homework_assignment, errors = await service.request_changes(
        assignment_id=assignment_id,
        changes_schema=changes_schema,
    )

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return await make_homework_assignment_schema(homework_assignment)


@router.get(
    '/by-room-post/{assigned_room_post_id}',
    response_model=list[HomeworkAssignmentDetailSchema],
    operation_id='getAssignmentsForRoomPost',
    status_code=status.HTTP_200_OK,
)
async def fetch_post_assignments(
    assigned_room_post_id: int,
    user: User = Depends(get_current_user),
):
    service = HomeworkAssignmentService(user)

    homework_assignments, _ = await service.fetch_for_teacher(
        assigned_room_post_id=assigned_room_post_id,
    )
    return [
        await make_homework_assignment_schema(assignment)
        for assignment in homework_assignments
    ]


@router.post(
    '/{assignment_id}/reassign',
    response_model=HomeworkAssignmentDetailSchema,
    operation_id='reassignHomework',
    status_code=status.HTTP_200_OK,
)
async def reassign_homework(
    assignment_id: int,
    user: User = Depends(get_current_user),
):
    service = HomeworkAssignmentService(user)

    homework_assignment, errors = await service.reassign(
        assignment_id=assignment_id,
    )

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return await make_homework_assignment_schema(homework_assignment)


@router.post(
    '/{assignment_id}/rate',
    response_model=HomeworkAssignmentDetailSchema,
    operation_id='rateHomework',
    status_code=status.HTTP_200_OK,
)
async def mark_assignment_as_done(
    assignment_id: int,
    changes_schema: HomeworkAssignmentRateSchema,
    user: User = Depends(get_current_user),
):
    service = HomeworkAssignmentService(user)

    homework_assignment, errors = await service.mark_as_done(
        assignment_id=assignment_id,
        changes_schema=changes_schema,
    )

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return await make_homework_assignment_schema(homework_assignment)


@router.post(
    '/{assignment_id}/attachments',
    response_model=list[AttachmentListItemSchema],
    status_code=status.HTTP_201_CREATED,
    operation_id='attachFilesToAssignment',
)
async def attach_files_to_assignment(
    assignment_id: int,
    attachments: list[UploadFile],
    user: User = Depends(get_current_user),
):
    attachments_list = []
    attachment_service = AttachmentService(user)

    for attachment in attachments:
        attachments_list.append(
            AttachmentCreateSchema(
                filename=attachment.filename,
                source=await attachment.read(),
            ),
        )
    attachments, errors = await attachment_service.create_for_homework_assignment(
        attachments_list,
        assignment_id,
    )

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return [AttachmentListItemSchema.from_orm(attachment) for attachment in attachments]
