from core.common.containers import MainContainer


container = MainContainer()
container.wire(
    packages=['core.scheduler.tasks'],
)
