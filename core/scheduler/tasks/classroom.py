from dependency_injector.wiring import (
    inject,
    Provide,
)

from core.apps.classroom.schemas import RoomPostEmailNotificationSchema
from core.common.containers import MainContainer
from core.common.services.notifications import NotificationsService
from core.common.services.notifications.schemas import (
    NotificationClientSchema,
    SendNotificationSchema,
)
from core.scheduler.app import huey_app


@huey_app.task()
@inject
def notify_room_post_created(
    targets: list[str],
    room_post: RoomPostEmailNotificationSchema,
    notifications_service: NotificationsService = Provide[MainContainer.notifications_service],
):
    notifications_service.send_room_post_created(
        SendNotificationSchema(
            clients=[
                NotificationClientSchema(
                    email=email,
                    context={
                        'hyperlink': user.hyperlink,  # no qa
                        'first_name': user.first_name,  # no qa
                    },
                ) for email in targets
            ],
        ),
    )
