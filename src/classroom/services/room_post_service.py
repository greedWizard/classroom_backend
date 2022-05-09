from classroom.models import RoomPost
from classroom.services.base import AbstractRoomPostService

from core.config import config


class RoomPostService(AbstractRoomPostService):
    model = RoomPost
