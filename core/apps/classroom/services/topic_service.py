from collections import defaultdict
from typing import (
    Optional,
    Union,
)

from core.apps.classroom.models.participations import Participation
from core.apps.classroom.models.topics import Topic
from core.apps.classroom.repositories.participation_repository import ParticipationRepository
from core.apps.classroom.repositories.topic_repository import TopicRepository
from core.apps.classroom.schemas.topics import (
    TopicCreateSchema,
    TopicUpdateSchema,
)
from core.common.services.author import AuthorMixin
from core.common.services.base import CRUDService
from core.common.services.decorators import action


class TopicService(AuthorMixin, CRUDService):
    _repository: TopicRepository = TopicRepository()
    _participation_repository: ParticipationRepository = ParticipationRepository()

    async def _validate_manage_topics_in_room(
        self,
        room_id: int,
    ) -> dict[str, list]:
        errors = defaultdict(list)
        participation: Participation = await self._participation_repository.retrieve(
            room_id=room_id,
            user_id=self.user.id,
        )

        if participation is None:
            errors['room_id'].append(
                'Вы не присутствуете в данной комнате.',
            )
        elif not participation.can_create_topics:
            errors['author'].append(
                'У вас нет прав на редактирование учебного плана в данной комнате.',
            )
        return errors

    async def __validate_topic_create(
        self,
        room_id: int,
        title: str,
    ) -> tuple[bool, Optional[str]]:
        errors = await self._validate_manage_topics_in_room(room_id)

        if not title:
            errors['title'].append(
                'У темы обязательно должно быть название',
            )
        return errors

    async def __validate_fetch(self, room_id: int) -> dict:
        errors = defaultdict(list)

        participation: Participation = await self._participation_repository.retrieve(
            room_id=room_id,
            user_id=self.user.id,
        )

        if participation is None:
            errors['room_id'].append(
                'Вы не присутствуете в данной комнате.',
            )
        return errors

    async def __validate_topic_update(
        self,
        topic: Topic,
    ) -> dict:
        errors = defaultdict(list)

        if topic is None:
            errors['topic_id'].append('Данной темы не существует.')
        else:
            errors: dict = await self._validate_manage_topics_in_room(topic.room_id)

        return errors

    @action
    async def fetch_for_room(
        self,
        room_id: int,
        limit: Optional[int] = None,
        offset: int = 0,
        search: str = '',
    ) -> tuple[Optional[dict], Optional[list[Topic]]]:
        errors = await self.__validate_fetch(room_id)

        if len(errors) > 0:
            return None, errors

        return await self._repository.fetch_for_room(
            room_id=room_id,
            limit=limit,
            offset=offset,
            search=search,
        ), None

    @action
    async def update(
        self,
        id: Union[int, str],
        update_schema: TopicUpdateSchema,
        join: list[str] = None,
        **kwargs,
    ) -> tuple[Topic, dict]:
        errors = await self.__validate_topic_update(
            topic=await self._repository.retrieve(id=id),
        )

        if len(errors) > 0:
            return None, errors

        update_kwargs = update_schema.dict(exclude_unset=True, exclude_none=True)
        topic = await self._repository.update_with_order(
            topic_id=id,
            join=join,
            **update_kwargs,
        )
        return topic, None

    @action
    async def create(
        self,
        create_schema: TopicCreateSchema,
        exclude_unset: bool = False,
        join: list[str] = None,
    ) -> tuple[Topic, dict]:
        errors = await self.__validate_topic_create(
            room_id=create_schema.room_id,
            title=create_schema.title,
        )

        if len(errors) > 0:
            return None, errors

        max_order = await self._repository.count(room_id=create_schema.room_id) + 1
        return await self._repository.create(
            join=join,
            order=max_order,
            author_id=self.user.id,
            **create_schema.dict(exclude_unset=exclude_unset),
        ), None

    @action
    async def delete_and_displace_orders(self, id: int):
        errors = defaultdict(list)
        topic: Topic = await self._repository.retrieve(id=id)

        if not topic:
            errors['topic_id'].append('Данной темы не существует.')
        errors |= await self._validate_manage_topics_in_room(room_id=topic.room_id)

        if len(errors) > 0:
            return None, errors
        else:
            await self._repository.delete_and_displace_orders([topic])
        return None, errors
