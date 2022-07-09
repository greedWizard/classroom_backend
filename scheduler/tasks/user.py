from dependency_injector.wiring import (
    inject,
    Provide,
)
from jinja2 import Environment
from scheduler.app import huey_app
from scheduler.tasks.subjects import (
    USER_ACTIVATION_SUBJECT,
    USER_PASSWORD_RESET_SUBJECT,
)

from apps.common.containers import (
    MainContainer,
    TemplatesContainer,
)
from apps.common.services.email import EmailService
from apps.user.schemas import UserHyperlinkEmailSchema


@huey_app.task()
@inject
def send_activation_email(
    user: UserHyperlinkEmailSchema,
    email_service: EmailService = Provide[MainContainer.email_service],
    template_env: Environment = Provide[TemplatesContainer.env],
):
    template = template_env.get_template('user/Activation.html')
    body = template.render(user=user)

    email_service.send_email(
        subject=USER_ACTIVATION_SUBJECT,
        recipients=[user.email],
        body=body,
    )


@huey_app.task()
@inject
def send_password_reset_email(
    user: UserHyperlinkEmailSchema,
    email_service: EmailService = Provide[MainContainer.email_service],
    template_env: Environment = Provide[TemplatesContainer.env],
):
    template = template_env.get_template('user/PasswordReset.html')
    body = template.render(user=user)

    email_service.send_email(
        subject=USER_PASSWORD_RESET_SUBJECT,
        recipients=[user.email],
        body=body,
    )
