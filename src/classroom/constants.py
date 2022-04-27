from enum import Enum


class ParticipationRoleEnum(Enum):
    moderator = 'moderator'
    host = 'host'
    participant = 'participant'


class HomeWorkAssignmentStatus(Enum):
    not_passed = 'not passed'
    passed = 'passed'
    done = 'done'
    change_request = 'changes requested'
