from dependency_injector import (
    containers,
    providers,
)
from itsdangerous import TimedSerializer

from core.common.config import config
from core.common.helpers.image_resizer import ImageResizer
from core.common.integrations.base import HTTPXClient
from core.common.services.notifications import NotificationsService


class MainContainer(containers.DeclarativeContainer):
    wiring_config: containers.WiringConfiguration = containers.WiringConfiguration(
        modules=[
            'core.scheduler.tasks.classroom',
            'core.common.utils',
            'core.apps.users.services.user_service',
            'core.apps.users.utils',
        ],
    )

    mail_client = providers.Factory(
        HTTPXClient,
        base_url=config.NOTIFICATIONS_BASE_URL,
    )
    notifications_service = providers.Factory(
        NotificationsService,
        client=mail_client,
    )
    timed_serializer = providers.Factory(
        TimedSerializer,
        secret_key=config.APP_SECRET_KEY,
    )

    image_resizer = providers.Factory(
        ImageResizer,
    )
