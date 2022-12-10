from typing import Callable

from fastapi import (
    FastAPI,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi_pagination import add_pagination

from core.apps.localization.middlewares import localization_middleware
from core.common.config import config
from core.common.exception_handlers import authjwt_exception_handler


API_V1_PREFIX = '/api/v1/'


class AppFactory:
    @classmethod
    def add_middleware(
        cls,
        app: FastAPI,
        protocol: str,
        middleware: Callable[[Request, Callable], None],
    ):
        app.middleware(protocol)(middleware)

    @classmethod
    def create_app(cls) -> FastAPI:
        """Returns the FastAPI app with instantiated DB."""
        app = FastAPI(
            debug=config.DEBUG_MODE,
            title='Classroom API',
        )

        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.ALLOWED_CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )
        cls._register_views(app)
        cls.add_middleware(app, 'http', localization_middleware)

        app.exception_handler(AuthJWTException)(authjwt_exception_handler)

        add_pagination(app)
        return app

    @classmethod
    def _register_views(cls, app: FastAPI):
        from core.apps.attachments.views import router as attachment_router
        from core.apps.chat.views import router as chat_router
        from core.apps.classroom.views import router as classroom_router
        from core.apps.localization.views import router as localization_router
        from core.apps.users.views import router as user_router

        app.include_router(
            localization_router,
            prefix=''.join([API_V1_PREFIX, 'localization']),
        )
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
