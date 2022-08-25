from typing import (
    Optional,
    Union,
)

from fastapi import (
    Depends,
    UploadFile,
)
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from fastapi_pagination import (
    Page,
    paginate,
)

from starlette import status

from core.apps.attachments.schemas import (
    AttachmentCreateSchema,
    AttachmentListItemSchema,
)
from core.apps.attachments.services.attachment_service import AttachmentService
from core.apps.classroom.schemas import (
    HomeworkAssignmentCreateSchema,
    HomeworkAssignmentDetailSchema,
    HomeworkAssignmentRateSchema,
    HomeworkAssignmentRequestChangesSchema,
)
from core.apps.classroom.schemas.assignments import (
    HomeworkAssignmentCreateSuccessSchema,
    HomeworkAssignmentListitemSchema,
)
from core.apps.classroom.services.homework_assignment_service import AssignmentService
from core.apps.users.dependencies import get_current_user
from core.apps.users.models import User


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
    service = AssignmentService(user)
    homework_assignment, errors = await service.create(create_schema)

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return homework_assignment


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
    service = AssignmentService(user)
    homework_assignment, errors = await service.request_changes(
        assignment_id=assignment_id,
        changes_schema=changes_schema,
    )

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return homework_assignment


@router.get(
    '',
    response_model=Page[HomeworkAssignmentListitemSchema],
    operation_id='fetchAssignments',
    status_code=status.HTTP_200_OK,
)
async def fetch_assignments(
    post_id: Union[int, None] = None,
    room_id: Union[int, None] = None,
    user: User = Depends(get_current_user),
):
    service = AssignmentService(user)
    errors = None
    assignments = []

    if post_id is not None:
        assignments, errors = await service.fetch_post_assignments(
            post_id=post_id,
            join=['author'],
        )
    elif room_id is not None:
        assignments, errors = await service.fetch_room_assignments(
            room_id=room_id,
            join=['author'],
        )

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return paginate(assignments)


@router.get(
    '/{assignment_id}',
    response_model=HomeworkAssignmentDetailSchema,
    operation_id='get',
    status_code=status.HTTP_200_OK,
)
async def get_assignment(
    assignment_id: int,
    user: User = Depends(get_current_user),
):
    service = AssignmentService(user)
    assignment, errors = await service.retrieve_detail(assignment_id)

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=errors,
        )
    return assignment


@router.get(
    '/my/{post_id}',
    response_model=Optional[HomeworkAssignmentDetailSchema],
    operation_id='myInPost',
    status_code=status.HTTP_200_OK,
)
async def get_my_assignment(
    post_id: int,
    user: User = Depends(get_current_user),
):
    service = AssignmentService(user)

    assignment = await service.retrieve_user_assignment_for_post(
        post_id=post_id,
        join=['author', 'post', 'post.room', 'attachments'],
    )
    return assignment


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
    service = AssignmentService(user)

    homework_assignment, errors = await service.reassign(
        assignment_id=assignment_id,
    )

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return homework_assignment


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
    service = AssignmentService(user)

    homework_assignment, errors = await service.mark_as_done(
        assignment_id=assignment_id,
        changes_schema=changes_schema,
    )

    if errors:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=errors)
    return homework_assignment


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
