from apps.classroom.models import RoomPost
from apps.classroom.services.base import AbstractRoomPostService


class RoomPostService(AbstractRoomPostService):
    model = RoomPost
