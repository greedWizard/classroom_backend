import logging

from core.apps.users.containers import UserContainer
from core.common.factory import AppFactory


# SQLALCHEMY LOGGER
sqla_logger = logging.getLogger('sqlalchemy')
sqla_handler = logging.FileHandler('logs/sql.log')
sqla_handler.setLevel(logging.INFO)
sqla_logger.addHandler(sqla_handler)

# APP LOGGER
app_logger = logging.getLogger('fastapi')
app_handler = logging.FileHandler('logs/fastapi.log')

user_container = UserContainer()
user_container.wire(modules=['core.apps.users.utils'])

app = AppFactory.create_app()
