# TODO: Dependency injection
from typing import (
    Any,
    List,
    NewType,
)

from common.services.email.clients import SMTPClient


AbstractMailClient = NewType('AbstractMailClient', Any)


class EmailService:
    def __init__(self, mail_client: SMTPClient):
        self.mail_client = mail_client

    def send_email(
        self,
        subject: str,
        recipients: List[str],
        body: str,
        subtype: str = 'html',
    ):
        self.mail_client.send_email(
            subject=subject,
            recipients=recipients,
            body=body,
            subtype=subtype,
        )
