# from apps.chat.containers import ChatContainer
from apps.common.factory import AppFactory
from apps.user.containers import UserContainer


# ChatContainer()
user_container = UserContainer()
user_container.wire(
    modules=['apps.user.utils'],
)

app = AppFactory.create_app()
