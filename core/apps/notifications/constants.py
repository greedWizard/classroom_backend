from enum import Enum


class NotificationTypes(str, Enum):
    message = 'new message'
    joined_user = 'user joined'
