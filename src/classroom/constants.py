from enum import Enum


class ParticipationRoleEnum(str, Enum):
    moderator = 'moderator'
    host = 'teacher'
    participant = 'student'


class HomeWorkAssignmentStatus(str, Enum):
    passed = 'passed'
    done = 'done'
    request_changes = 'changes requested'


class RoomPostType(str, Enum):
    material = 'material'
    homework = 'homework'
