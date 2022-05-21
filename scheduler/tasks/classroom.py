from scheduler.app import huey_app
from scheduler.extensions import run_async_task


@run_async_task
@huey_app.task()
def send_email(
    email_content: str,
    recipients: list[str],
):
    pass
