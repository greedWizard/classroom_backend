from abc import ABC
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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

    def _form_html_message(
        self,
        subject: str,
        recipient: str,
        body: str,
    ):
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = self.config.mail_from
        message['To'] = recipient

        mime_html = MIMEText(body, 'html')
        message.attach(mime_html)

        return message

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
                message = self._form_html_message(
                    subject=subject,
                    recipient=recipient,
                    body=body,
                )

                server.sendmail(
                    self.config.mail_from,
                    recipient,
                    message.as_string(),
                )
