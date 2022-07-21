from apps.classroom.models import RoomPost
from apps.common.repositories.base import CRUDRepository


class RoomPostRepository(CRUDRepository):
    _model: type[RoomPost] = RoomPost
