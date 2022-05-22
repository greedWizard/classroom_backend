from huey import RedisHuey

from common.config.huey import huey_settings
from common.containers import (
    MainContainer,
    TemplatesContainer,
)


main_container = MainContainer()
main_container.wire(
    packages=['scheduler.tasks'],
)
templates_container = TemplatesContainer()
templates_container.wire(
    packages=['scheduler.tasks'],
)
huey_app = RedisHuey(
    name=huey_settings.redis_name,
    url=huey_settings.redis_url,
    utc=True,
    immediate=False,
)
