import os
from typing import Dict, List

from fastapi import FastAPI
from fastapi_pagination import add_pagination
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth.exceptions import AuthJWTException

from tortoise import Tortoise
from tortoise.contrib.fastapi import register_tortoise

from core.config import config
from core.exception_handlers import authjwt_exception_handler


Tortoise.init_models(config.MODELS_PATHS, config.MODELS_APP_LABEL)

API_V1_PREFIX = '/api/v1/'


class AppFactory:
    @classmethod
    def create_app(cls, test_mode: bool = False) -> FastAPI:
        ''' Returns the FastAPI app with instantiated DB '''
        app = FastAPI(
            debug=os.environ.get('LATERON_DEBUG', config.DEBUG_MODE),
            title=os.environ.get('LATERON_TITLE', 'Homework Test'),
        )

        DB_URL = config.DB_CONNECTION_STRING if not test_mode \
            else config.DB_TEST_CONNECTION_STRING

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
        import classroom.views
        import user.views
        import attachment.views

        app.include_router(
            user.views.router,
            prefix=''.join([API_V1_PREFIX, 'auth/user']),
        )
        app.include_router(
            classroom.views.router,
            prefix=''.join([API_V1_PREFIX, 'classroom']),
        )
        app.include_router(
            attachment.views.router,
            prefix=''.join([API_V1_PREFIX, 'attachments']),
        )
