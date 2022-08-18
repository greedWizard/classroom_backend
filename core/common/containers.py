from dependency_injector import (
    containers,
    providers,
)
from itsdangerous import TimedSerializer
from jinja2 import (
    Environment,
    FileSystemLoader,
)

from core.common.config import config
from core.common.config.integrations import MailClientConnectionConfig
from core.common.helpers.image_resizer import ImageResizer
from core.common.services.email import EmailService
from core.common.services.email.clients import SMTPClient


class TemplatesContainer(containers.DeclarativeContainer):
    wiring_config: containers.WiringConfiguration = containers.WiringConfiguration(
        modules=[
            'core.scheduler.tasks.classroom',
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
            'core.scheduler.tasks.classroom',
            'core.common.utils',
            'core.apps.users.services.user_service',
            'core.apps.users.utils',
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
    timed_serializer = providers.Singleton(
        TimedSerializer,
        secret_key=config.APP_SECRET_KEY,
    )

    image_resizer = providers.Singleton(
        ImageResizer,
    )
