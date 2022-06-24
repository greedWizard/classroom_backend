from dependency_injector.wiring import (
    inject,
    Provide,
)
from jinja2 import Environment
from scheduler.app import huey_app
from scheduler.tasks.subjects import USER_ACTIVATION_SUBJECT

from apps.common.containers import (
    MainContainer,
    TemplatesContainer,
)
from apps.common.services.email import EmailService
from apps.user.schemas import UserActivationEmailSchema


@huey_app.task()
@inject
def send_activation_email(
    user: UserActivationEmailSchema,
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
