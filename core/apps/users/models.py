import sqlalchemy as sa

from core.common.models.base import BaseDBModel


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
    phone_number = sa.Column(sa.String(15), unique=True)
    email = sa.Column(sa.String(255), unique=True)
    gender = sa.Column(sa.String(50))
    is_banned = sa.Column(sa.Boolean, default=False)
    last_login = sa.Column(sa.DateTime)

    is_reset_needed = sa.Column(sa.Boolean, default=False)
    password_reset_deadline = sa.Column(sa.DateTime)
    profile_picture_path = sa.Column(sa.String, default='')

    # INTEGRATIONS
    vk_user_id = sa.Column(sa.Integer)

    def __str__(self) -> str:
        return (
            f'{self.first_name} {self.last_name} {self.email}'
        )

    def __repr__(self) -> str:
        return f'<User {self.first_name} {self.last_name} {self.email} active={self.is_active}>'

    @property
    def full_name(self):
        return f'{self.first_name} {self.middle_name} {self.last_name}'
