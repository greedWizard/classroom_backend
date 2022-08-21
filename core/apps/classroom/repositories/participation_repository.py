from sqlalchemy import select

from core.apps.classroom.models import Participation
from core.common.repositories.base import CRUDRepository


class ParticipationRepository(CRUDRepository):
    _model: type[Participation] = Participation

    async def count_room_members(self, room_id: int):
        return await self.count(room_id=room_id)

    async def get_user_roommates(self, user_id: int) -> list[int]:
        async with self.get_session() as session:
            user_room_ids_subquery = select(self._model.room_id).filter(
                self._model.user_id == user_id,
            )
            roomates_ids_select = select(self._model.user_id).filter(
                self._model.room_id.in_(user_room_ids_subquery),
            )
            roommates_ids = await session.execute(roomates_ids_select)
            roommates_ids = roommates_ids.scalars().unique().all()
            roommates_ids.remove(user_id)
            return roommates_ids

    async def is_user_roommate(self, user_id: int, other_user_id: int) -> bool:
        return other_user_id in await self.get_user_roommates(user_id=user_id)

    async def are_users_rommmates(self, users_ids: list[int]) -> bool:
        users_ids_length = len(users_ids)
        are_roommates = True

        for user_index in range(users_ids_length-1):
            for other_user_index in range(user_index+1, users_ids_length):
                if not await self.is_user_roommate(
                    user_id=users_ids[user_index],
                    other_user_id=users_ids[other_user_index],
                ):
                    are_roommates = False
                    break
            if not are_roommates:
                break
        return are_roommates
