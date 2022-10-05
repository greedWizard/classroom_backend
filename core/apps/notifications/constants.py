from enum import Enum


class NotificationTypes(str, Enum):
    message = 'new message'
    room_join = 'user joined'
    post_added = 'teacher added a new post'
