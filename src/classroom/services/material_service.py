from classroom.models import HomeWork, Material
from classroom.services.base import AbstractRoomPostService


class MaterialService(AbstractRoomPostService):
    model = Material


class HomeWorkService(AbstractRoomPostService):
    model = HomeWork
