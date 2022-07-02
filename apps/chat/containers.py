from dependency_injector import providers
from dependency_injector.containers import (
    DeclarativeContainer,
    WiringConfiguration,
)

from apps.chat.managers import ChatManager


class ChatContainer(DeclarativeContainer):
    wiring_config: WiringConfiguration = WiringConfiguration(
        modules=['.views'],
    )
    manager = providers.Singleton(
        ChatManager,
    )
