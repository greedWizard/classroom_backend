from typing import List

from tortoise.expressions import Q

from apps.attachment.exceptions import AttachmentMaxSizeException
from apps.attachment.models import Attachment
from apps.attachment.schemas import AttachmentCreateSchema
from apps.classroom.models import (
    HomeworkAssignment,
    Participation,
    Room,
    RoomPost,
)
from apps.common.config import config
from apps.common.services.author import AuthorMixin
from apps.common.services.base import CRUDService
from apps.common.services.decorators import action
from apps.user.models import User


# TODO: здесь всё ужасно, нужен рефакторинг
class AttachmentService(AuthorMixin, CRUDService):
    model = Attachment
    room_model = Room
    participation_model = Participation
    room_post_model = RoomPost
    homework_assignment_model = HomeworkAssignment
    user_model = User

    async def get_queryset(self, management: bool = False):
        moder_roles = self.participation_model.MODERATOR_ROLES
        expression = (
            Q(
                assignments__assigned_room_post__room__participations__role__in=moder_roles,  # no qa
            )
            | Q(author_id=self.user.id)
            | Q(
                room_posts__room_id__in=await self.user.participations.all().values_list(
                    'room_id',
                    flat=True,
                ),
            )
        )

        if management:
            expression &= Q(
                room_posts__room__participations__role__in=self.participation_model.MODERATOR_ROLES,
            ) | Q(author_id=self.user.id)

        return self.model.filter(
            id__in=await self.model.filter(expression).values_list('id', flat=True),
        )

    async def _can_attach_to_room_post(self, room_post_id: int):
        return await self.participation_model.can_moderate(self.user, room_post_id)

    async def validate_room_post_id(self, value: int):
        if not await self._can_attach_to_room_post(value):
            return False, 'You can not moderate this room.'
        return True, None

    async def _create_attachable_files(
        self,
        attachmentCreateSchemaList: List[AttachmentCreateSchema],
    ):
        for attachment in attachmentCreateSchemaList:
            if len(attachment.source) > config.MAX_FILE_SIZE:
                raise AttachmentMaxSizeException(
                    f'{attachment.filename} file is to large.',
                )

        attachments = [
            await self.model(
                filename=attachmentCreateSchema.filename,
                source=attachmentCreateSchema.source,
                author_id=self.user.id,
                updated_by_id=self.user.id,
            )
            for attachmentCreateSchema in attachmentCreateSchemaList
        ]

        for attachment in attachments:
            await attachment.save()
        return attachments

    @action
    async def create_for_room_post(
        self,
        attachmentCreateSchemaList: List[AttachmentCreateSchema],
        room_post_id: int,
    ):
        # TODO: как-то можно обощить все методы для присоединения файлов
        room_post = await self.room_post_model.get(id=room_post_id)

        try:
            attachments = await self._create_attachable_files(
                attachmentCreateSchemaList,
            )
        except AttachmentMaxSizeException as e:
            return False, {'attachment': str(e)}

        if not room_post:
            return False, {'room_post_id': 'Room post not found'}
        if not await self._can_attach_to_room_post(room_post_id):
            return False, {'room_post_id': 'You can not moderate this room.'}

        await room_post.attachments.add(*attachments)
        return attachments, None

    @action
    async def create_for_homework_assignment(
        self,
        attachmentCreateSchemaList: List[AttachmentCreateSchema],
        assignment_id: int,
    ):
        # TODO: как-то можно обощить все методы для присоединения файлов
        assignment = await self.homework_assignment_model.filter(
            id=assignment_id,
            author_id=self.user.id,
        ).first()

        if not assignment:
            return False, {'assignment_id': 'Assignment not found'}

        try:
            attachments = await self._create_attachable_files(
                attachmentCreateSchemaList,
            )
        except AttachmentMaxSizeException as e:
            return False, e

        await assignment.attachments.add(*attachments)
        return attachments, None
