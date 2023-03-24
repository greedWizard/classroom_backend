from dependency_injector.wiring import (
    inject,
    Provide,
)

from core.apps.users.schemas import UserHyperlinkEmailSchema
from core.common.containers import MainContainer
from core.common.services.notifications import NotificationsService
from core.common.services.notifications.schemas import (
    NotificationClientSchema,
    SendNotificationSchema,
)
from core.scheduler.app import huey_app


@huey_app.task()
@inject
def send_activation_email(
    user: UserHyperlinkEmailSchema,
    localization: str,
    notifications_service: NotificationsService = Provide[MainContainer.notifications_service],
):
    notifications_service.send_registration_success(
        SendNotificationSchema(
            clients=[
                NotificationClientSchema(
                    email=user.email,
                    context={
                        'hyperlink': user.hyperlink,
                        'first_name': user.first_name,
                    },
                ),
            ],
            localization=localization,
        ),
    )


@huey_app.task()
@inject
def send_password_reset_email(
    user: UserHyperlinkEmailSchema,
    localization: str,
    notifications_service: NotificationsService = Provide[MainContainer.notifications_service],
):
    notifications_service.send_password_reset(
        SendNotificationSchema(
            clients=[
                NotificationClientSchema(
                    email=user.email,
                    context={
                        'hyperlink': user.hyperlink,
                        'first_name': user.first_name,
                    },
                ),
            ],
            localization=localization,
        ),
    )
