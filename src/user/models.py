import hashlib

from tortoise import fields
from tortoise.queryset import QuerySet

from core.models import TimeStampAbstract
from user.utils import hash_string


class User(TimeStampAbstract):
    id = fields.IntField(pk=True)
    first_name = fields.CharField(max_length=100)
    last_name = fields.CharField(max_length=100)
    middle_name = fields.CharField(max_length=100, blank=True, null=True)
    password = fields.CharField(null=True, blank=True, max_length=256)
    rating = fields.IntField(default=0)
    last_login = fields.DatetimeField(null=True, blank=True)
    activation_token = fields.CharField(max_length=256)
    activation_deadline_dt = fields.DatetimeField()
    is_active = fields.BooleanField(default=False)
    is_reset_needed = fields.BooleanField(default=False)
    phone_number = fields.CharField(max_length=15, unique=True)
    email = fields.CharField(max_length=255, unique=True)
    gender = fields.CharField(null=True, blank=True, max_length=50)

    class Meta:
        table = 'users'

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name} {self.email}'

    def __repr__(self) -> str:
        return f'<User {self.first_name} {self.last_name} {self.email}>'

    async def is_participating(self, room_id: int) -> bool:
        return await self.participations.filter(room_id=room_id).exists()
    
    async def set_password(self, unhashed_password: str):
        self.password = hash_string(unhashed_password)
        await self.save()

    @classmethod
    async def active(cls) -> QuerySet:
        ''' Get active users '''
        return cls.filter(is_active=True)
