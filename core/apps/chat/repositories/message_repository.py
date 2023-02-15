from typing import Optional

from sqlalchemy import (
    func,
    select,
)

from core.apps.chat.models import (
    DialogsParticipants,
    Message,
)
from core.common.repositories.base import CRUDRepository


class MessageRepository(CRUDRepository):
    _model: type[Message] = Message

    async def get_unique_last_messages(
        self,
        user_id: int,
        ordering: list[str] = None,
        join: list[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        **filters,
    ):
        statement = await self._fetch_statement(
            ordering=ordering,
            join=join,
            offset=offset,
            limit=limit,
            **filters,
        )

        distinc_dialogs_subquery = select(func.max(self._model.id))\
            .group_by(self._model.dialog_id)

        filter_participant_subquery = select(DialogsParticipants.c.dialog_id).filter(
            DialogsParticipants.c.user_id == user_id,
        )

        statement = statement.filter(self._model.id.in_(distinc_dialogs_subquery))
        statement = statement.filter(self._model.dialog_id.in_(filter_participant_subquery))

        async with self.get_session() as session:
            result = await session.execute(statement)
            return result.unique().scalars().all()
