from collections import defaultdict

from core.apps.classroom.constants import ParticipationRoleEnum
from core.apps.classroom.models import (
    Participation,
    RoomPost,
)
from core.apps.classroom.repositories.participation_repository import ParticipationRepository
from core.apps.classroom.repositories.post_repository import RoomPostRepository
from core.apps.classroom.repositories.room_repository import RoomRepository
from core.apps.classroom.repositories.topic_repository import TopicRepository
from core.apps.classroom.schemas import RoomPostEmailNotificationSchema
from core.apps.classroom.schemas.room_posts import (
    RoomPostCreateSchema,
    RoomPostCreateSuccessSchema,
    RoomPostUpdateSchema,
)
from core.apps.localization.utils import translate as _
from core.common.config import config
from core.common.services.author import AuthorMixin
from core.common.services.base import CRUDService
from core.common.services.decorators import action
from core.scheduler.tasks.classroom import notify_room_post_created


class RoomPostService(AuthorMixin, CRUDService):
    _repository: RoomPostRepository = RoomPostRepository()
    _participation_repository: ParticipationRepository = ParticipationRepository()
    _room_repository: RoomRepository = RoomRepository()
    _topic_repository: TopicRepository = TopicRepository()

    schema_map = {
        'create': RoomPostCreateSuccessSchema,
    }

    async def validate_description(self, value: str):
        if not value:
            return True, None
        if len(value) > config.DESCRIPTION_MAX_LENGTH:
            return (
                False,
                _(
                    'Description should be less than {TITLE_MAX_LENGTH}'
                    ' characters.',
                ).format(TITLE_MAX_LENGTH=config.TITLE_MAX_LENGTH),
            )
        return True, None

    async def validate_title(self, value: str):
        if not value:
            return False, _('This field is required')
        if len(value) > config.TITLE_MAX_LENGTH:
            return (
                False,
                _(
                    'Title should be less than {TITLE_MAX_LENGTH} characters.',
                ).format(TITLE_MAX_LENGTH=config.TITLE_MAX_LENGTH),
            )
        return True, None

    @action
    async def retrieve_detail(self, id: int):
        return await self.retrieve(
            ['attachments', 'assignments'],
            id=id,
        )

    async def _notify_room_post_create(self, room_post: RoomPost):
        emails = await room_post.room.participations.filter(
            role=ParticipationRoleEnum.participant,
        ).values_list(
            'user__email',
            flat=True,
        )
        email_subject = RoomPostEmailNotificationSchema.from_orm(room_post)
        email_subject.subject_link = config.FRONTEND_ROOM_POST_URL.format(
            post_id=room_post.id,
            room_id=room_post.room_id,
        )

        if room_post:
            notify_room_post_created(
                targets=emails,
                room_post=email_subject,
            )

    async def _check_participant_permission(
        self,
        participation: Participation,
    ):
        if not participation:
            return False
        return participation.can_manage_posts

    async def _get_participation_by_room_post(
        self,
        post_id: int,
    ) -> Participation:
        room_post: RoomPost = await self._repository.retrieve(id=post_id)
        return await self._participation_repository.retrieve(
            room_id=room_post.room_id,
            user_id=self.user.id,
        )

    @action
    async def fetch(
        self,
        _ordering,
        join: list[str] = None,
        limit: int = 50,
        offset: int = 0,
        search: str = '',
        **filters,
    ):
        if 'room_id' in filters:
            if not await self._participation_repository.count(
                room_id=filters['room_id'],
                user_id=self.user.id,
            ):
                return None, {'error': _('Access denied!')}

        if search:
            return await self._repository.search_fetch(
                _ordering,
                join,
                limit=limit,
                offset=offset,
                search=search,
                **filters,
            ), None
        return await super().fetch(_ordering, join, limit=limit, offset=offset, **filters)

    async def _validate_topic(
        self,
        topic_id: int,
        room_id: int,
    ) -> dict:
        errors = defaultdict(list)
        topic = await self._topic_repository.retrieve(id=topic_id)

        if topic is None:
            errors['topic_id'].append('Данной темы не существует.')
        elif topic.room_id != room_id:
            errors['topic_id'].append('Вы не можете добавить тему из другой комнаты.')
        return errors

    @action
    async def update(
        self,
        id: int,
        update_schema: RoomPostUpdateSchema,
        join: list[str] = None,
        exclude_unset: bool = True,
    ):
        participation = await self._get_participation_by_room_post(id)
        post = await self._repository.retrieve(
            join=join,
            id=id,
        )
        errors = defaultdict(list)

        if not await self._check_participant_permission(participation):
            errors['room_id'].append(_('You are not allowed to do that.'))
        if update_schema.topic_id is not None:
            errors |= await self._validate_topic(
                topic_id=update_schema.topic_id,
                room_id=post.room_id,
            )

        if errors:
            return None, errors

        return await super().update(id, update_schema, join, exclude_unset)

    @action
    async def create(
        self,
        create_schema: RoomPostCreateSchema,
        exclude_unset: bool = False,
        join: list[str] = None,
    ):
        participation: Participation = await self._participation_repository.retrieve(
            user_id=self.user.id,
            room_id=create_schema.room_id,
        )
        errors = defaultdict(list)

        if not await self._check_participant_permission(participation):
            errors['room_id'].append(_('You are not allowed to do that.'))
        if create_schema.topic_id is not None:
            errors |= await self._validate_topic(
                topic_id=create_schema.topic_id,
                room_id=create_schema.room_id,
            )

        if errors:
            return None, errors

        return await super().create(
            create_schema=create_schema,
            exclude_unset=exclude_unset,
            join=join,
        )

    @action
    async def delete(self, **filters):
        if 'id' in filters:
            post_id = filters['id']
            participation = await self._get_participation_by_room_post(post_id)

            if not await self._check_participant_permission(participation):
                return None, {'error': _('You are not allowed to do that.')}
        return await super().delete(**filters)
