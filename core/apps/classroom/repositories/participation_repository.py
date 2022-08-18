from core.apps.classroom.models import Participation
from core.common.repositories.base import CRUDRepository


class ParticipationRepository(CRUDRepository):
    _model: type[Participation] = Participation

    async def count_room_members(self, room_id: int):
        return await self.count(room_id=room_id)
