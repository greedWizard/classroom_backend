import os
from datetime import timedelta
from typing import (
    Dict,
    List,
)

import environ
from pydantic import BaseModel


env = environ.Env()


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
    POSTGRES_DB: str = env('POSTGRES_DB')
    POSTGRES_PORT: int = env('POSTGRES_PORT')

    DB_CONNECTION_STRING: str = f'postgres://{POSTGRES_USER_NAME}:{POSTGRES_USER_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
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
        'apps.attachment.models',
        'apps.user.models',
        'apps.classroom.models',
        'apps.chat.models',
    ]

    APP_MODULES: Dict[str, List[str]] = {
        MODELS_APP_LABEL: MODELS_PATHS,
    }
    MINIMAL_DAYS_DELTA: int = int(env('MINIMAL_DAYS_DELTA'))
    # APP SETTINGS

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
