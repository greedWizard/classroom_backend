import sqlalchemy as sa

from apps.common.database import DBModel
from apps.common.models import BaseMetaData


# TODO: info verbose name + translations
class User(DBModel, BaseMetaData):
    __tablename__ = 'users'

    first_name = sa.Column(sa.String(length=100), nullable=False)
    last_name = sa.Column(sa.String(length=100), nullable=False)
    middle_name = sa.Column(sa.String(length=100))
    password = sa.Column(sa.String(length=250), nullable=False)
    activation_token = sa.Column(sa.String(256), nullable=False)
    activation_deadline_dt = sa.Column(sa.DateTime)
    is_active = sa.Column(sa.Boolean, default=False)
    is_reset_needed = sa.Column(sa.Boolean, default=False)
    phone_number = sa.Column(sa.String(15), unique=True, nullable=False)
    email = sa.Column(sa.String(255), unique=True, nullable=False)
    gender = sa.Column(sa.String(50))
    is_banned = sa.Column(sa.Boolean, default=False)
    last_login = sa.Column(sa.DateTime)

    class Meta:
        table = 'users'

    def __str__(self) -> str:
        return (
            f'{self.first_name} {self.last_name} {self.email} active={self.is_active}'
        )

    def __repr__(self) -> str:
        return f'<User {self.first_name} {self.last_name} {self.email} active={self.is_active}>'

    async def is_participating(self, room_id: int) -> bool:
        return await self.participations.filter(room_id=room_id).exists()

    @property
    def full_name(self):
        return f'{self.first_name} {self.middle_name} {self.last_name}'
