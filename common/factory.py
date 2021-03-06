import os

from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi_pagination import add_pagination
from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from common.config import config
from common.exception_handlers import authjwt_exception_handler


Tortoise.init_models(config.MODELS_PATHS, config.MODELS_APP_LABEL)

API_V1_PREFIX = '/api/v1/'


class AppFactory:
    @classmethod
    def create_app(cls, test_mode: bool = False) -> FastAPI:
        """Returns the FastAPI app with instantiated DB."""
        app = FastAPI(
            debug=os.environ.get('LATERON_DEBUG', config.DEBUG_MODE),
            title=os.environ.get('LATERON_TITLE', 'Homework Test'),
        )

        DB_URL = (
            config.DB_CONNECTION_STRING
            if not test_mode
            else config.DB_TEST_CONNECTION_STRING
        )

        register_tortoise(
            app,
            db_url=DB_URL,
            modules=config.APP_MODULES,
            generate_schemas=True,
            add_exception_handlers=True,
        )

        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.ALLOWED_CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )
        cls._register_views(app)

        app.exception_handler(AuthJWTException)(authjwt_exception_handler)

        add_pagination(app)
        return app

    @classmethod
    def _register_views(cls, app: FastAPI):
        from apps.attachment.views import router as attachment_router
        from apps.chat.views import router as chat_router
        from apps.classroom.views import router as classroom_router
        from apps.user.views import router as user_router

        app.include_router(
            user_router,
            prefix=''.join([API_V1_PREFIX, 'auth/user']),
        )
        app.include_router(
            classroom_router,
            prefix=''.join([API_V1_PREFIX, 'classroom']),
        )
        app.include_router(
            attachment_router,
            prefix=''.join([API_V1_PREFIX, 'attachments']),
        )
        app.include_router(
            chat_router,
            prefix=''.join([API_V1_PREFIX, 'chat']),
        )
