from apps.chat.containers import ChatContainer
from apps.common.factory import AppFactory


ChatContainer()
app = AppFactory.create_app()
