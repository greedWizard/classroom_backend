from huey import RedisHuey

from core.common.config import config


huey_app = RedisHuey(
    name=config.CACHE_SERVICE_HOST,
    url=config.CACHE_URL,
    utc=True,
    immediate=config.HUEY_IMMEDIATE,
)
