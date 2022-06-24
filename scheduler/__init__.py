from apps.common.containers import (
    MainContainer,
    TemplatesContainer,
)


container = MainContainer()
container.wire(
    packages=['scheduler.tasks'],
)
templates_container = TemplatesContainer()
templates_container.wire(
    packages=['scheduler.tasks'],
)
