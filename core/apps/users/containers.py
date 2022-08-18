from fastapi_jwt_auth import AuthJWT

from dependency_injector import providers
from dependency_injector.containers import (
    DeclarativeContainer,
    WiringConfiguration,
)


class UserContainer(DeclarativeContainer):
    wiring_config: WiringConfiguration = WiringConfiguration(
        modules=[
            'core.apps.users.views',
            'core.apps.users.dependencies',
            'core.apps.users.utils',
        ],
    )
    jwt_auth = providers.Factory(AuthJWT)