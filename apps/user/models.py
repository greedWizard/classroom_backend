import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref

from apps.common.models.base import BaseDBModel

from apps.common.utils import get_attachment_path


# TODO: info verbose name + translations
class User(BaseDBModel):
    __tablename__ = 'users'

    first_name = sa.Column(sa.String(length=100), nullable=False)
    last_name = sa.Column(sa.String(length=100), nullable=False)
    middle_name = sa.Column(sa.String(length=100))
    password = sa.Column(sa.String(length=250), nullable=False)
    activation_token = sa.Column(sa.String(256), nullable=False)
    activation_deadline_dt = sa.Column(sa.DateTime)
    is_active = sa.Column(sa.Boolean, default=False)
    phone_number = sa.Column(sa.String(15), unique=True, nullable=False)
    email = sa.Column(sa.String(255), unique=True, nullable=False)
    gender = sa.Column(sa.String(50))
    is_banned = sa.Column(sa.Boolean, default=False)
    last_login = sa.Column(sa.DateTime)

    profile_picture_id = sa.Column(sa.Integer(), sa.ForeignKey('attachments.id', use_alter=True))

    is_reset_needed = sa.Column(sa.Boolean, default=False)
    password_reset_deadline = sa.Column(sa.DateTime)

    def __str__(self) -> str:
        return (
            f'{self.first_name} {self.last_name} {self.email} active={self.is_active}'
        )

    def __repr__(self) -> str:
        return f'<User {self.first_name} {self.last_name}{self.email} active={self.is_active}>'

    @property
    def full_name(self):
        return f'{self.first_name} {self.middle_name} {self.last_name}'

    # TODO remove hardcode
    @property
    def profile_picture_path(self) -> str:
        return get_attachment_path(self.profile_picture_id)
