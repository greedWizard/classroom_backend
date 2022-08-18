from enum import Enum


class ParticipationRoleEnum(str, Enum):
    moderator = 'moderator'
    host = 'teacher'
    participant = 'student'


class HomeWorkAssignmentStatus(str, Enum):
    assigned = 'assigned'
    done = 'done'
    request_changes = 'changes requested'


class RoomPostType(str, Enum):
    material = 'material'
    homework = 'homework'


ASSIGNMENTS_MANAGER = 'moderator'
ASSIGNMENT_AUTHOR = 'author'

ASSIGNMENT_STATUS_MUTATIONS: dict[str, dict[str, list[str]]] = {
    HomeWorkAssignmentStatus.assigned: {
        ASSIGNMENTS_MANAGER: [
            HomeWorkAssignmentStatus.done,
            HomeWorkAssignmentStatus.request_changes,
        ],
        ASSIGNMENT_AUTHOR: [
            HomeWorkAssignmentStatus.assigned,
        ],
    },
    HomeWorkAssignmentStatus.request_changes: {
        ASSIGNMENTS_MANAGER: [
            HomeWorkAssignmentStatus.done,
        ],
        ASSIGNMENT_AUTHOR: [
            HomeWorkAssignmentStatus.assigned,
        ],
    },
}
