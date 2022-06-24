from dependency_injector import (
    containers,
    providers,
)
from jinja2 import (
    Environment,
    FileSystemLoader,
)

from apps.common.config import config
from apps.common.config.integrations import MailClientConnectionConfig
from apps.common.services.email import EmailService
from apps.common.services.email.clients import SMTPClient


class TemplatesContainer(containers.DeclarativeContainer):
    wiring_config: containers.WiringConfiguration = containers.WiringConfiguration(
        modules=[
            'scheduler.tasks.classroom',
        ],
    )
    file_loader: FileSystemLoader = providers.Factory(
        FileSystemLoader,
        searchpath=config.JINJA_TEMPLATES_FOLDER,
    )
    env: Environment = providers.Factory(
        Environment,
        loader=file_loader,
    )


class MainContainer(containers.DeclarativeContainer):
    wiring_config: containers.WiringConfiguration = containers.WiringConfiguration(
        modules=[
            'scheduler.tasks.classroom',
        ],
    )

    mail_client_config = providers.Factory(MailClientConnectionConfig)
    mail_client = providers.Singleton(
        SMTPClient,
        config=mail_client_config,
    )
    email_service = providers.Singleton(
        EmailService,
        mail_client=mail_client,
    )
