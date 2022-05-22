from common.containers import (
    MainContainer,
    TemplatesContainer,
)


container = MainContainer()
container.wire(
    modules=['scheduler.tasks.classroom'],
)
templates_container = TemplatesContainer()
templates_container.wire(
    modules=['scheduler.tasks.classroom'],
)
