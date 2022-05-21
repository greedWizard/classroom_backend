from fastapi_jwt_auth import AuthJWT

from .settings import (
    JWTSettings,
    ProjectSettings,
)


@AuthJWT.load_config
def get_config():
    return JWTSettings()


try:
    config = ProjectSettings()
except FileNotFoundError:
    raise FileNotFoundError('No .env file found')
