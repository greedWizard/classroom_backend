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
    MessageSchema,
)
from apps.chat.services.dialog_service import DialogService
from apps.chat.services.message_service import MessageService
from apps.user.dependencies import websocket_user


router = APIRouter(tags=['chat'])


# TODO: логировать здесь ВСЁ абсолютно, творится какая-то херня
@router.websocket('/')
@inject
async def chat(
    websocket: WebSocket,
    jwt_token: str = Query(...),
    reciever_id: int = Query(...),
    dialog_service: DialogService = Depends(DialogService),
    chat_manager: ChatManager = Depends(Provide[ChatContainer.manager]),
    message_service: MessageService = Depends(),
):
    user = await websocket_user(token=jwt_token)
    exists, dialog = await dialog_service.check_dialog_exists(
        sender_id=user.id,
        reciever_id=reciever_id,
    )

    if not exists:
        dialog, _ = await dialog_service.create(
            DialogCreateSchema(
                sender_id=user.id,
                reciever_id=reciever_id,
            ),
        )
    await chat_manager.connect(websocket=websocket, dialog=dialog)
    messages = [MessageSchema.from_orm(message) for message in dialog.messages]
    await chat_manager.broadcast(messages, dialog)

    try:
        while True:
            data = await websocket.receive_json()
            message, _ = await message_service.create(
                MessageCreateSchema(
                    sender_id=user.id,
                    reciever_id=reciever_id,
                    text=data['message'],
                    dialog_id=dialog.id,
                ),
                fetch_related=['sender', 'reciever'],
            )
            messages.append(MessageSchema.from_orm(message))
            await chat_manager.broadcast(messages, dialog)
    except (ConnectionClosedError, WebSocketDisconnect):
        await chat_manager.disconnect(websocket, dialog)
