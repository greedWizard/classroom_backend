from pydantic import (
    BaseSettings,
    Field,
)


class MailClientConnectionConfig(BaseSettings):
    mail_username: str = Field(..., env='SMTP_MAIL_FROM')
    mail_password: str = Field(..., env='SMTP_PASSWORD')
    mail_from: str = Field(..., env='SMTP_MAIL_FROM')
    mail_server: str = Field(..., env='SMTP_MAIL_SERVER')
    mail_port: int = Field(default=465, env='SMTP_MAIL_PORT')
    mail_debug: int = Field(default=0, env='SMTP_DEBUG_MODE')
    mail_tls: bool = Field(default=True, env='MAIL_TLS')
    mail_ssl: bool = Field(default=False, env='MAIL_SSL')
    use_credentials: bool = Field(default=True, env='USE_CREDENTIALS')
    validate_certs: bool = Field(default=True, env='VALIDATE_CERTS')
