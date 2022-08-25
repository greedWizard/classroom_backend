from core.apps.users.containers import UserContainer
from core.common.factory import AppFactory


user_container = UserContainer()
user_container.wire(
    modules=['core.apps.users.utils'],
)

app = AppFactory.create_app()
