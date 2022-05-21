from huey import RedisHuey

from common.config.huey import huey_settings


huey_app = RedisHuey(
    name=huey_settings.redis_name,
    url=huey_settings.redis_url,
    utc=True,
)
