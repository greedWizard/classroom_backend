import os

from fastapi_mail import ConnectionConfig


yandex_smtp_config = ConnectionConfig(
    MAIL_USERNAME = os.environ.get('YANDEX_SMTP_USERNAME'),
    MAIL_PASSWORD = os.environ.get('YANDEX_SMTP_PASSWORD'),
    MAIL_FROM = os.environ.get('YANDEX_SMTP_MAIL_FROM'),
    MAIL_PORT = os.environ.get('YANDEX_SMTP_MAIL_PORT', 465),
    MAIL_SERVER = os.environ.get('YANDEX_SMTP_MAIL_SERVER'),
    MAIL_DEBUG = int(os.environ.get('YANDEX_SMTP_DEBUG_MODE'), 0),
    MAIL_TLS = True,
    MAIL_SSL = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True,
)
