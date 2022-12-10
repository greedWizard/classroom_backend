from core.apps.cache.services import RedisCacheService
from core.common.config import config


class LocalizationService:
    _cache_service: RedisCacheService = RedisCacheService()
    translate_language: str = config.DEFAULT_LANGUAGE

    @classmethod
    async def set_localization_to_client(cls, localization_code: str, client_address: str):
        if localization_code not in config.SUPPORTED_LANGUAGES:
            return False, {'localization': 'Language is not supported.'}

        await cls._cache_service.set_cache(client_address, localization_code.encode())
        return True, None

    @classmethod
    async def get_client_localization(cls, client_address: str) -> str:
        return (await cls._cache_service.get_cache(client_address) or config.DEFAULT_LANGUAGE).decode()
