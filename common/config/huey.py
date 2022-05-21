from pydantic import (
    BaseSettings,
    Field,
)


class HueySettings(BaseSettings):
    redis_name: str = Field(..., env='SCHEDULER_NAME')
    redis_url: str = Field(..., env='SCHEDULER_REDIS_URL')


huey_settings = HueySettings()
