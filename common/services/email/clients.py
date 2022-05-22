from abc import ABC
from dataclasses import dataclass
from smtplib import SMTP
from typing import (
    Any,
    List,
    NewType,
)

from common.config.integrations import MailClientConnectionConfig


AbstractMailClient = NewType('AbstractMailClient', Any)


class AbstractMailClient(ABC):
    def __init__(self, config: MailClientConnectionConfig):
        ...

    def send_email(
        self,
        subject: str,
        recipients: List[str],
        body: str,
        subtype: str = 'html',
    ):
        ...


@dataclass
class SMTPClient(AbstractMailClient):
    config: MailClientConnectionConfig

    @property
    def email_message(self) -> str:
        return (
            'From: {sender_email}\nTo: {destination_email}'
            '\nSubject: {subject}\n\n{body}'
        )

    def send_email(
        self,
        subject: str,
        recipients: List[str],
        body: str,
        subtype: str = 'html',
    ):
        with SMTP(self.config.mail_server, self.config.mail_port) as server:
            server.ehlo()
            server.starttls()
            server.login(self.config.mail_username, self.config.mail_password)
            server.set_debuglevel(1)

            for recipient in recipients:
                server.sendmail(
                    self.config.mail_from,
                    recipient,
                    self.email_message.format(
                        destination_email=recipient,
                        subject=subject,
                        body=body,
                        sender_email=self.config.mail_from,
                    ),
                )
