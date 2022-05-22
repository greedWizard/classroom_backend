from common.containers import MainContainer


container = MainContainer()
container.wire(
    modules=['scheduler.tasks.classroom'],
)
