from dependency_injector.wiring import (
    inject,
    Provide,
)
from websockets.exceptions import ConnectionClosedError

from fastapi import (
    APIRouter,
    Depends,
    Query,
    WebSocket,
    WebSocketDisconnect,
)

from apps.chat.containers import ChatContainer
from apps.chat.managers import ChatManager
from apps.chat.schemas import (
    DialogCreateSchema,
    MessageCreateSchema,
    MessageListItemSchema,
)
from apps.chat.services.dialog_service import DialogService
from apps.chat.services.message_service import MessageService
from apps.user.dependencies import (
    get_current_user,
    websocket_user,
)
from apps.user.models import User


router = APIRouter(tags=['chat'])


# TODO: логировать здесь ВСЁ абсолютно, творится какая-то херня
@router.websocket('/')
@inject
async def chat(
    websocket: WebSocket,
    jwt_token: str = Query(...),
    reciever_id: int = Query(...),
    sender_id: int = Query(...),
    chat_manager: ChatManager = Depends(Provide[ChatContainer.manager]),
):
    user = await websocket_user(token=jwt_token)

    dialog_service = DialogService(user)
    message_service = MessageService(user)

    exists, dialog = await dialog_service.get_dialog(
        sender_id=sender_id,
        reciever_id=reciever_id,
    )

    if not exists:
        dialog, _ = await dialog_service.create(
            DialogCreateSchema(reciever_id=reciever_id),
            fetch_related=DialogService.fields_for_chat,
        )
    await chat_manager.connect(websocket=websocket, dialog=dialog)
    await chat_manager.broadcast_dialog(dialog)

    try:
        while True:
            data = await websocket.receive_json()
            message, _ = await message_service.create(
                MessageCreateSchema(
                    reciever_id=reciever_id,
                    text=data['message'],
                    dialog_id=dialog.id,
                ),
                fetch_related=['sender', 'reciever'],
            )
            # TODO: можно ли как-то присылать актуальные сообщения не обновляя весь диалог?
            _, dialog = await dialog_service.get_dialog(
                sender_id=sender_id,
                reciever_id=reciever_id,
            )
            await chat_manager.broadcast_dialog(dialog)
    except (ConnectionClosedError, WebSocketDisconnect):
        await chat_manager.disconnect(websocket, dialog)


# TODO: тесты на эту вьюху
@router.get(
    '/my-dialogs',
    response_model=list[MessageListItemSchema],
    operation_id='myDialogs',
)
async def my_dialogs(
    user: User = Depends(get_current_user),
):
    message_service = MessageService(user)
    messages = await message_service.fetch_last()

    return [MessageListItemSchema.from_orm(message) for message in messages]
