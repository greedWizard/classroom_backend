from typing import NewType, Union
from tortoise import models, fields
from tortoise.exceptions import NoValuesFetched
from tortoise.expressions import Q

from classroom.constants import ParticipationRoleEnum
from core.models import AuthorAbstract, TimeStampAbstract


UserModel = NewType('UserModel', models.Model)


class Room(TimeStampAbstract, AuthorAbstract):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=1000)
    description = fields.TextField(blank=True, null=True)
    join_slug = fields.CharField(max_length=256)

    class Meta:
        table = 'rooms'

    def __str__(self) -> str:
        return f'{self.name[:50]} {self.description}'

    def __repr__(self) -> str:
        return f'<{self.name[:50]} {self.description}>'

    @property
    def participations_count(self) -> int:
        try:
            return len(self.participations)
        except NoValuesFetched:
            return 0

    def join_full_link(self) -> str:
        return f'/api/v1/classroom/join/{self.join_slug}'


class Participation(TimeStampAbstract, AuthorAbstract):
    id = fields.IntField(pk=True)
    room = fields.ForeignKeyField('models.Room', related_name='participations', on_delete=fields.CASCADE)
    user = fields.ForeignKeyField('models.User', related_name='participations', on_delete=fields.CASCADE)
    role = fields.CharEnumField(enum_type=ParticipationRoleEnum, default=ParticipationRoleEnum.participant.name)

    MODERATOR_ROLES = (
        ParticipationRoleEnum.host, ParticipationRoleEnum.moderator,
    )

    def can_moderate_room(self) -> bool:
        return self.role == ParticipationRoleEnum.moderator or \
            self.role == ParticipationRoleEnum.host

    @classmethod
    async def is_user_moderator(
        cls,
        user: Union[int, UserModel],
        room: Union[int, Room],
    ):
        user_id = getattr(user, 'id', user)
        room_id = getattr(room, 'id', room)
        
        return await cls.filter(
            user_id=user_id,
            room_id=room_id,
            role__in=cls.MODERATOR_ROLES, 
        )

    @classmethod
    async def can_moderate(
        cls,
        user: Union[int, UserModel],
        material: Union[int, Room],
    ):
        user_id = getattr(user, 'id', user)
        material_id = getattr(material, 'id', material)

        return await cls.filter(
            user_id=user_id,
            room__materials__id=material_id,
            role__in=cls.MODERATOR_ROLES,
        ).exists()

    @classmethod
    async def is_participating(
        cls,
        user_id: int,
        room_id: int,
    ):
        return await cls.filter(room_id=room_id, user_id=user_id).exists()

    class Meta:
        table = 'participations'
        unique_together = (
            ('room', 'user')
        )


class RoomPostAbstract(AuthorAbstract, TimeStampAbstract):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=1000)
    description = fields.TextField(blank=True, null=True)

    class Meta:
        abstract = True


class Material(RoomPostAbstract):
    text = fields.TextField(null=True, blank=True)
    room = fields.ForeignKeyField('models.Room', related_name='materials', on_delete=fields.CASCADE)
    attachments = fields.ManyToManyField(
        'models.Attachment',
        related_name='materials',
        through='materials_attachments',
    )

    def __str__(self) -> str:
        return f'"{self.title}" / "{self.description}"'

    def __repr__(self) -> str:
        return f'<Material {str(self)}>'

    class Meta:
        table = 'materials'


class HomeWork(RoomPostAbstract):
    room = fields.ForeignKeyField(
        'models.Room',
        related_name='homeworks',
        on_delete=fields.CASCADE,
    )
    deadline_at = fields.DatetimeField(blank=True, null=True)
    receipt_dt = fields.DatetimeField(auto_now_add=True)
    attachments = fields.ManyToManyField(
        'models.Attachment',
        related_name='homeworks',
        through='homeworks_attachments',
    )

    class Meta:
        table = 'homeworks'


class HomeworkAssignment(TimeStampAbstract, AuthorAbstract):
    id = fields.IntField(pk=True)
    attachments = fields.ManyToManyField(
        'models.Attachment',
        related_name='homework_assignments',
        through='homeworkassignments_attachments',
    )
    comment = fields.TextField()
    homework = fields.ForeignKeyField(
        'models.HomeWork',
        related_name='assignments',
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = 'homework_assignments'
