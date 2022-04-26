# TODO: Dependency injection
from typing import List
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from core.config.integrations import yandex_smtp_config


class EmailService:
    def __init__(self) -> None:
        self.mail_client = FastMail(yandex_smtp_config)

    async def send_email(
        self,
        subject: str,
        recipients: List[str],
        body: str,
        subtype: str = 'html',
    ):
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=body,
            subtype=subtype,
        )
        await self.mail_client.send_message(message)
        return 0
