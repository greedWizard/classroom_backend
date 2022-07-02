from apps.classroom.models import HomeworkAssignment
from apps.common.repositories.base import CRUDRepository


class HomeworkAssignmentRepository(CRUDRepository):
    _model: type[HomeworkAssignment] = HomeworkAssignment
