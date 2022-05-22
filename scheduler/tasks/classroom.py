from dependency_injector.wiring import (
    inject,
    Provide,
)
from jinja2 import Environment
from scheduler.app import huey_app
from scheduler.tasks.email_messages import ROOM_POST_NOTIFICATION_CREATED

from apps.classroom.schemas import RoomPostCreateEmailSchema
from common.containers import (
    MainContainer,
    TemplatesContainer,
)
from common.services.email import EmailService


@huey_app.task()
@inject
def notify_room_post_created(
    targets: list[str],
    room_post: RoomPostCreateEmailSchema,
    email_service: EmailService = Provide[MainContainer.email_service],
    template_env: Environment = Provide[TemplatesContainer.env],
):
    template = template_env.get_template()
    body = template.render(room_post=room_post)

    email_service.send_email(
        subject=ROOM_POST_NOTIFICATION_CREATED,
        recipients=targets,
        body=body,
    )
