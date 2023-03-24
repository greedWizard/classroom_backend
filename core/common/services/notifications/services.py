from dataclasses import dataclass
from typing import (
    Any,
    NewType,
)

from core.common.config import config
from core.common.integrations.base import IClient
from core.common.services.notifications.schemas import SendNotificationSchema


AbstractMailClient = NewType('AbstractMailClient', Any)


@dataclass
class NotificationsService:
    client: IClient

    def send_registration_success(
        self,
        registration_success_schema: SendNotificationSchema,
    ) -> None:
        self.client.post(
            uri=config.NOTIFICATIONS_REGISTRATION_SUCCESS_URI,
            json=registration_success_schema.dict(exclude_unset=True),
        )

    def send_password_reset(
        self,
        registration_success_schema: SendNotificationSchema,
    ) -> None:
        self.client.post(
            uri=config.NOTIFICATIONS_PASSWORD_RESET_URI,
            json=registration_success_schema.dict(exclude_unset=True),
        )
