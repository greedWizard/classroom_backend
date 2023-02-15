from typing import Callable

from fastapi import Request

from core.apps.localization.services import LocalizationService


async def localization_middleware(request: Request, call_next: Callable):
    LocalizationService.translate_language = await LocalizationService.get_client_localization(
        request.client.host,
    )
    return await call_next(request)
