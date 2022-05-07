from enum import Enum


class ParticipationRoleEnum(str, Enum):
    moderator = 'moderator'
    host = 'host'
    participant = 'participant'


class HomeWorkAssignmentStatus(str, Enum):
    not_passed = 'not passed'
    passed = 'passed'
    done = 'done'
    change_request = 'changes requested'


class RoomPostType(str, Enum):
    material = 'material'
    homework = 'homework'
