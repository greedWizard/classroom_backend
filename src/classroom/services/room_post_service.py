from classroom.models import RoomPost
from classroom.services.base import AbstractRoomPostService


class RoomPostService(AbstractRoomPostService):
    model = RoomPost
