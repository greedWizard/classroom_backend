from pydantic import BaseModel


class NotificationClientSchema(BaseModel):
    email: str = ''
    push_client_id: str = ''
    context: dict


class SendNotificationSchema(BaseModel):
    clients: list[NotificationClientSchema]
    localization: str
