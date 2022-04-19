from typing import List

from tortoise.expressions import Q
from attachment.models import Attachment
from attachment.schemas import AttachmentCreateSchema
from classroom.constants import ParticipationRoleEnum

from classroom.models import HomeWork, HomeworkAssignment, Material, Participation, Room

from core.services.author import AuthorMixin
from core.services.base import CRUDService
from core.services.decorators import action

from user.models import User


class AttachmentService(AuthorMixin, CRUDService):
    model = Attachment
    room_model = Room
    participation_model = Participation
    material_model = Material
    homework_model = HomeWork
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
            Q(materials__room_id__in=user_rooms_ids) | \
            Q(homeworks__room_id__in=user_rooms_ids) | \
            Q(homework_assignments__homework__room_id__in=user_rooms_ids)
        ).values_list('id', flat=True)
        return self.model.filter(id__in=attachment_ids)

    def __init__(self, user: User, *args, **kwargs) -> None:
        super().__init__(user, *args, **kwargs)
    
    async def _can_attach_to_material(self, material_id: int):
        return await self.participation_model.can_moderate(self.user, material_id)

    async def validate_material_id(self, value: int):
        if not await self._can_attach_to_material(value):
            return False, 'You can not moderate this room.'
        return True, None

    @action
    async def create_for_material(
        self,
        listAttachmentCreateSchema: List[AttachmentCreateSchema],
        material_id: int,
    ):
        if not await self._can_attach_to_material(material_id):
            return False, { 'material_id': 'You can not moderate this room.' }

        material = await self.material_model.get(id=material_id)
        attachments = [await self.model(
            filename=attachmentCreateSchema.filename,
            source=attachmentCreateSchema.source,
            author_id=self.user.id,
            updated_by_id=self.user.id,
        ) for attachmentCreateSchema in listAttachmentCreateSchema]

        for attachment in attachments:
            await attachment.save()

        await material.attachments.add(*attachments)
        await material.fetch_related('attachments', 'author')
        return material, None
