from dependency_injector import (
    containers,
    providers,
)

from core.apps.integrations.authentications.vk.client import VKIntegratioinClient
from core.common.config import config


class IntegrationContainer(containers.DeclarativeContainer):
    wiring_config: containers.WiringConfiguration = containers.WiringConfiguration(
        modules=[
            'core.apps.users.views',
            'core.apps.users.services.user_service',
        ],
    )
    vk_integration_client: VKIntegratioinClient = providers.Factory(
        VKIntegratioinClient,
        client_id=config.VK_CLIENT_ID,
        client_secret=config.VK_CLIENT_SECRET,
        redirect_uri=config.VK_REDIRECT_URI,
    )
