import sqlalchemy as sa

from core.common.models.base import BaseDBModel


class Notification(BaseDBModel):
    summary = sa.Column(
        sa.String(length=300, null=False),
    )
    type = sa.Column(
        sa.Enum(

        ),
    )
