from apps.chat.containers import ChatContainer
from common.factory import AppFactory


ChatContainer()
app = AppFactory.create_app()
