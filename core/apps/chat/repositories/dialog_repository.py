from typing import Optional

from sqlalchemy import (
    case,
    func,
    insert,
    select,
)

from core.apps.chat.models import (
    Dialog,
    DialogsParticipants,
)
from core.common.repositories.base import CRUDRepository


class DialogRepository(CRUDRepository):
    _model: Dialog = Dialog

    async def add_participants_to_dialog(
        self,
        dialog_id: int,
        participants_ids: list[int],
    ) -> int:
        async with self.get_session() as session:
            query = insert(DialogsParticipants)

            await session.execute(
                query, [
                    {'dialog_id': dialog_id, 'user_id': participant_id}
                                    for participant_id in participants_ids
                ],
            )
            await session.commit()
        return len(participants_ids)

    async def find_exact_dialog(
        self,
        users_ids: list[int],
        join: Optional[list[str]] = None,
    ) -> Optional[Dialog]:
        sub_statement = select(DialogsParticipants.c.dialog_id).group_by(
            DialogsParticipants.c.dialog_id,
        ).having(
            func.count(DialogsParticipants.c.dialog_id) == func.sum(
                case(
                    (DialogsParticipants.c.user_id.in_(users_ids), 1),
                    else_=0,
                ),
            ),
        )
        statement = select(self._model).filter(self._model.id.in_(sub_statement))
        statement = await self._join_statement(statement, join)

        async with self.get_session() as session:
            result = await session.execute(statement)
            return result.scalar()
