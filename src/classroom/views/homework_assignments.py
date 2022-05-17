from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter

from starlette import status

from classroom.schemas import HomeworkAssignmentCreateSchema, HomeworkAssignmentCreateSuccessSchema
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
