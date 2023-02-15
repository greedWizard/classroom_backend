import json
from functools import cached_property
from typing import (
    Protocol,
    Union,
)

from redis import Redis

from core.common.config import config


class AbstractCacheService(Protocol):
    @cached_property
    def client(self):
        ...

    async def set_cache(self, key: str, value: str):
        raise NotImplementedError()

    async def set_json_cache(self, key: str, value: Union[dict, list]):
        json_data = json.dumps(value)
        return self.set_cache(key, json_data)

    async def get_cache(self, key: str) -> str:
        raise NotImplementedError()

    async def get_json_cache(self, key: str) -> Union[dict, list]:
        json_data = json.loads(self.get_cache(key))
        return json_data


class RedisCacheService(AbstractCacheService):
    @cached_property
    def client(self):
        return Redis(host=config.CACHE_SERVICE_HOST, port=config.CACHE_SERVICE_PORT)

    async def set_cache(self, key: str, value: str):
        self.client.set(key, value)

    async def get_cache(self, key: str) -> str:
        return self.client.get(key)
