from core.apps.chat.managers import ChatManager
from dependency_injector import providers
from dependency_injector.containers import (
    DeclarativeContainer,
    WiringConfiguration,
)


class ChatContainer(DeclarativeContainer):
    wiring_config: WiringConfiguration = WiringConfiguration(
        modules=['.views'],
    )
    manager = providers.Singleton(
        ChatManager,
    )
