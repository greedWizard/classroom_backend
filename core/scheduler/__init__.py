from core.common.containers import (
    MainContainer,
    TemplatesContainer,
)


container = MainContainer()
container.wire(
    packages=['core.scheduler.tasks'],
)
templates_container = TemplatesContainer()
templates_container.wire(
    packages=['core.scheduler.tasks'],
)
