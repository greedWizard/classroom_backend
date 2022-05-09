from typing import Dict, List
from datetime import timedelta
import environ
import os

from pydantic import BaseModel


env = environ.Env()
environ.Env.read_env(
    os.environ.get('LATERON_ENV_FILE_PATH', 'core/config/.env')
)


class JWTSettings(BaseModel):
    authjwt_secret_key: str = env('AUTHJWT_SECRET_KEY')


class ProjectSettings(BaseModel):
    # DEBUG SETTINGS
    DEBUG_MODE: bool = env('DEBUG_MODE')
    # END DEBUG SETTINGS

    # DB SETTINGS
    POSTGRES_HOST: str = env('POSTGRES_HOST')
    POSTGRES_USER_NAME: str = env('POSTGRES_USER')
    POSTGRES_USER_PASSWORD: str = env('POSTGRES_PASSWORD')
    POSTGRES_DATABASE: str = env('POSTGRES_DATABASE')
    POSTGRES_TEST_DATABASE: str = env('POSTGRES_TEST_DATABASE')
    POSTGRES_PORT: int = env('POSTGRES_PORT')

    DB_CONNECTION_STRING: str = f'postgres://{POSTGRES_USER_NAME}:{POSTGRES_USER_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}'
    DB_TEST_CONNECTION_STRING: str = 'sqlite://:memory:'
    # END DB SETTINGS

    # CLEANUP SETTINGS
    CLEANUP_TIMEOUT: int = env('CLEANUP_TIMEOUT')
    # END CLEANUP SETTINGS

    # CORS SETTINGS
    ALLOWED_CORS_ORIGINS: List[str] = env.list('ALLOWED_CORS_ORIGINS')
    # END CORS SETTINGS

    # APP SETTINGS
    MODELS_APP_LABEL: str = 'models'
    MODELS_PATHS: List[str] = [
        'attachment.models',
        'user.models',
        'classroom.models',
        'attachment.models',
        'chat.models',
    ]

    APP_MODULES: Dict[str, List[str]] = {
        MODELS_APP_LABEL: MODELS_PATHS
    }
    MINIMAL_DAYS_DELTA: int = int(env('MINIMAL_DAYS_DELTA'))

    # USER SETTINGS
    MINIMAL_PASSWORD_LENGTH: int = 10
    ACTIVATION_DEADLINE_HOURS: int = 3
    USER_SUCCESS_STATUS: str = 'success'
    USER_PERMISSION_DENIED_ERROR: str = 'You are not logged in.'
    AUTHORIZATION_TOKEN_EXPIRES_TIMEDELTA: timedelta = timedelta(days=3)
    
    # ETERNAL SETTINGS
    FRONTEND_LOGIN_URL: str = os.environ.get('FRONTEND_LOGIN_URL')

    # FILE SETTINGS
    MAX_FILE_SIZE: int = 64 * 1024 * 1024

    # POSTS SETTINGS
    TITLE_MAX_LENGTH: int = 150
    DESCRIPTION_MAX_LENGTH: int = 500
