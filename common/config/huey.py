from pydantic import (
    BaseSettings,
    Field,
)


class HueySettings(BaseSettings):
    redis_name: str = Field(..., env='SCHEDULER_NAME')
    redis_url: str = Field(..., env='SCHEDULER_REDIS_URL')
    immediate: str = Field(default=1, env='HUEY_IMMEDIATE')


huey_settings = HueySettings()
