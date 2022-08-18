from core.apps.classroom.models import RoomPost
from core.common.repositories.base import CRUDRepository


class RoomPostRepository(CRUDRepository):
    _model: type[RoomPost] = RoomPost
