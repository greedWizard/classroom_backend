from core.apps.classroom.schemas import RoomPostEmailNotificationSchema
from core.common.containers import (
    MainContainer,
    TemplatesContainer,
)
from core.common.services.email import EmailService
from core.scheduler.app import huey_app
from core.scheduler.tasks.subjects import ROOM_POST_NOTIFICATION_CREATED
from dependency_injector.wiring import (
    inject,
    Provide,
)
from jinja2 import Environment


@huey_app.task()
@inject
def notify_room_post_created(
    targets: list[str],
    room_post: RoomPostEmailNotificationSchema,
    email_service: EmailService = Provide[MainContainer.email_service],
    template_env: Environment = Provide[TemplatesContainer.env],
):
    template = template_env.get_template('classroom/RoomPostCreated.html')
    body = template.render(room_post=room_post)

    email_service.send_email(
        subject=ROOM_POST_NOTIFICATION_CREATED,
        recipients=targets,
        body=body,
    )
