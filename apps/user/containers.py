from dependency_injector import providers
from dependency_injector.containers import (
    DeclarativeContainer,
    WiringConfiguration,
)
from fastapi_jwt_auth import AuthJWT


class UserContainer(DeclarativeContainer):
    wiring_config: WiringConfiguration = WiringConfiguration(
        modules=[
            'apps.user.views',
            'apps.user.dependencies',
            'apps.user.utils',
        ],
    )
    jwt_auth = providers.Factory(AuthJWT)
