from typing import List

from tortoise.expressions import Q
from attachment.models import Attachment
from attachment.schemas import AttachmentCreateSchema

from classroom.models import HomeworkAssignment, RoomPost, Participation, Room

from core.services.author import AuthorMixin
from core.services.base import CRUDService
from core.services.decorators import action

from user.models import User


class AttachmentService(AuthorMixin, CRUDService):
    model = Attachment
    room_model = Room
    participation_model = Participation
    room_post_model = RoomPost
    homework_assignment_model = HomeworkAssignment
    user_model = User

    async def get_queryset(self, for_delete: bool = False):
        room_expression = Q(user_id=self.user.id)

        if for_delete:
            room_expression &= Q(role__in=self.participation_model.MODERATOR_ROLES)

        user_rooms_ids = await self.participation_model.filter(
            room_expression,
        ).values_list('room_id', flat=True)

        attachment_ids = await self.model.filter(
            Q(room_posts__room_id__in=user_rooms_ids) | \
            Q(homeworks__room_id__in=user_rooms_ids) | \
            Q(homework_assignments__homework__room_id__in=user_rooms_ids)
        ).values_list('id', flat=True)
        return self.model.filter(id__in=attachment_ids)

    def __init__(self, user: User, *args, **kwargs) -> None:
        super().__init__(user, *args, **kwargs)
    
    async def _can_attach_to_room_post(self, room_post_id: int):
        return await self.participation_model.can_moderate(self.user, room_post_id)

    async def validate_room_post_id(self, value: int):
        if not await self._can_attach_to_room_post(value):
            return False, 'You can not moderate this room.'
        return True, None

    @action
    async def create_for_room_post(
        self,
        listAttachmentCreateSchema: List[AttachmentCreateSchema],
        room_post_id: int,
    ):
        if not await self._can_attach_to_room_post(room_post_id):
            return False, { 'room_post_id': 'You can not moderate this room.' }

        room_post = await self.room_post_model.get(id=room_post_id)
        attachments = [await self.model(
            filename=attachmentCreateSchema.filename,
            source=attachmentCreateSchema.source,
            author_id=self.user.id,
            updated_by_id=self.user.id,
        ) for attachmentCreateSchema in listAttachmentCreateSchema]

        for attachment in attachments:
            await attachment.save()

        await room_post.attachments.add(*attachments)
        await room_post.fetch_related('attachments', 'author')
        [attachment for attachment in room_post.attachments]
        return room_post, None
