import pathlib
from datetime import timedelta

import environ
from pydantic import BaseModel


env = environ.Env()


class JWTSettings(BaseModel):
    authjwt_secret_key: str = env('AUTHJWT_SECRET_KEY')


class ProjectSettings(BaseModel):
    # DEBUG SETTINGS
    DEBUG_MODE: bool = env('DEBUG_MODE')
    # END DEBUG SETTINGS

    APP_SECRET_KEY: str = env('APP_SECRET_KEY')
    BASE_DIR = pathlib.Path(__file__).parent.parent.parent.parent

    # DB SETTINGS
    POSTGRES_HOST: str = env('POSTGRES_HOST')
    POSTGRES_USER_NAME: str = env('POSTGRES_USER')
    POSTGRES_USER_PASSWORD: str = env('POSTGRES_PASSWORD')
    POSTGRES_DB: str = env('POSTGRES_DB')
    POSTGRES_PORT: int = env('POSTGRES_PORT')
    DB_PREFIX: str = 'postgresql+asyncpg'

    DB_CONNECTION_STRING: str = (
        f'{DB_PREFIX}://{POSTGRES_USER_NAME}:'
        f'{POSTGRES_USER_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
    )
    DB_TEST_CONNECTION_STRING: str = 'sqlite+aiosqlite://'
    TEST_MODE: bool = bool(int(env('TEST_MODE', default=0)))
    # END DB SETTINGS

    # CLEANUP SETTINGS
    CLEANUP_TIMEOUT: int = env('CLEANUP_TIMEOUT')
    # END CLEANUP SETTINGS

    # CORS SETTINGS
    ALLOWED_CORS_ORIGINS: list[str] = env.list('ALLOWED_CORS_ORIGINS')
    # END CORS SETTINGS

    # APP SETTINGS
    MODELS_APP_LABEL: str = 'models'
    MODELS_PATHS: list[str] = [
        'core.apps.attachments.models',
        'core.apps.users.models',
        'core.apps.classroom.models',
        'core.apps.chat.models',
    ]

    APP_MODULES: dict[str, list[str]] = {
        MODELS_APP_LABEL: MODELS_PATHS,
    }
    MINIMAL_DAYS_DELTA: int = env('MINIMAL_DAYS_DELTA')
    PASSWORD_RESET_SALT: str = 'reset'
    RESET_PASSWORD_TIMEDELTA: timedelta = timedelta(minutes=30)
    # END APP SETTINGS

    # USER SETTINGS
    MINIMAL_PASSWORD_LENGTH: int = 10
    ACTIVATION_DEADLINE_HOURS: int = 3
    USER_SUCCESS_STATUS: str = 'success'
    USER_PERMISSION_DENIED_ERROR: str = 'You are not logged in.'
    AUTHORIZATION_TOKEN_EXPIRES_TIMEDELTA: timedelta = timedelta(days=3)

    # EXTERNAL SETTINGS
    FRONTEND_LOGIN_URL: str = env('FRONTEND_LOGIN_URL')
    FRONTEND_ROOM_POST_URL: str = env('FRONTEND_ROOM_POST_URL')
    FRONTEND_USER_RESET_PASSWORD_URL: str = env(
        'FRONTEND_USER_RESET_PASSWORD_URL',
    )
    FRONTEND_PASSWORD_RECOVERY_URL: str = env('FRONTEND_PASSWORD_RECOVERY_URL')

    # FILE SETTINGS
    MAX_FILE_SIZE: int = 64 * 1024 * 1024
    PROFILE_PICTURE_RESOLUTION = 200

    # POSTS SETTINGS
    TITLE_MAX_LENGTH: int = 150
    DESCRIPTION_MAX_LENGTH: int = 500

    # TEMPLATES
    JINJA_TEMPLATES_FOLDER: str = 'core/scheduler/mail/templates/'

    # STATIC
    STATIC_URL = env('STATIC_URL')
    DEFAULT_PROFILE_PICTURE_URL = env('DEFAULT_PROFILE_PICTURE_URL')

    # LOCALIZATION
    SUPPORTED_LANGUAGES = ['en', 'ru']
    LOCALE_DIR: str = BASE_DIR / 'locales'
    DEFAULT_LANGUAGE: str = 'en'

    CACHE_SERVICE_HOST: str = env('CACHE_SERVICE_HOST')
    CACHE_SERVICE_PORT: str = env('CACHE_SERVICE_PORT')
    CACHE_URL: str = env('SCHEDULER_REDIS_URL')
    HUEY_IMMEDIATE: bool = env('HUEY_IMMEDIATE', bool)

    # CERTBOT
    WELL_KNOWN_PATH = '/var/www/certbot/{file_name}'

    # OAUTH
    OUATH2_TOKEN_URL = '/api/v1/auth/user/authenticate'
    TOKEN_TYPE = 'bearer'
