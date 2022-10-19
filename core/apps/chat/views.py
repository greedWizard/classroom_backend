from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    WebSocket,
    WebSocketDisconnect,
)

from dependency_injector.wiring import (
    inject,
    Provide,
)
from starlette import status

from core.apps.chat.containers import ChatContainer
from core.apps.chat.managers import ChatManager
from core.apps.chat.repositories.dialog_repository import DialogRepository
from core.apps.chat.schemas import (
    DialogDetailSchema,
    DialogStartSchema,
    MessageCreateSchema,
    MessageDetailSchema,
)
from core.apps.chat.services.dialog_service import DialogService
from core.apps.chat.services.message_service import MessageService
from core.apps.users.dependencies import (
    get_current_user,
    get_websocket_user,
)
from core.apps.users.models import User


router = APIRouter(tags=['chat'])


@router.websocket('/')
@inject
async def chat(
    websocket: WebSocket,
    jwt_token: str = Query(...),
    dialog_id: int = Query(...),
    chat_manager: ChatManager = Depends(Provide[ChatContainer.manager]),
    dialog_repository: DialogRepository = Depends(DialogRepository),
    message_service: MessageService = Depends(MessageService),
):
    user = await get_websocket_user(token=jwt_token)
    await chat_manager.add_connection(dialog_id, websocket)

    if not await dialog_repository.check_participant_in_dialog(user.id, dialog_id):
        await websocket.close()
        raise WebSocketDisconnect(403)

    previous_messages, _ = await message_service.fetch(
        _ordering=['created_at'],
        join=['sender'],
        dialog_id=dialog_id,
    )
    await chat_manager.broadcast_batch(previous_messages, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            message_create_schema = MessageCreateSchema(
                text=data['text'],
                sender_id=user.id,
                dialog_id=dialog_id,
            )
            message, _ = await message_service.create(message_create_schema, join=['sender'])
            await chat_manager.broadcast_message_to_all_participants(message)
    except WebSocketDisconnect:
        await chat_manager.remove_connection(dialog_id, websocket)


@router.websocket('/all-dialogs/')
@inject
async def all_dialogs_preview(
    websocket: WebSocket,
    jwt_token: str = Query(...),
    chat_manager: ChatManager = Depends(Provide[ChatContainer.manager]),
    message_service: MessageService = Depends(MessageService),
):
    # TODO: подключить кафку и отправлять новые сообщение в реалтайме
    user = await get_websocket_user(token=jwt_token)
    messages = await message_service.get_unique_last_messages(
        user_id=user.id,
        join=['sender'],
    )

    for dialog_id in [message.dialog_id for message in messages]:
        await chat_manager.add_connection(dialog_id, websocket)

    try:
        await chat_manager.broadcast_batch(messages, websocket)
        data = await websocket.receive_json()
    except WebSocketDisconnect:
        for dialog_id in [message.dialog_id for message in messages]:
            await chat_manager.remove_connection(dialog_id=dialog_id, websocket=websocket)


@router.post(
    '/start-private-dialog',
    response_model=DialogDetailSchema,
    status_code=status.HTTP_201_CREATED,
    operation_id='startDialogWithTeacher',
    summary='Start a new private dialog',
    description='Creates a dialog with participants.'
    'If a dialog already exists between'
    'participants then it won\'t be created',
)
async def start_dialog(
    schema: DialogStartSchema,
    current_user: User = Depends(get_current_user),
    dialog_service: DialogService = Depends(),
):
    dialog, errors = await dialog_service.start_dialog(
        participants_ids=schema.participants_ids,
        author_id=current_user.id,
        join=['participants', 'author'],
    )

    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=errors,
        )
    return dialog


@router.get(
    '/last-messages',
    response_model=list[MessageDetailSchema],
    status_code=status.HTTP_200_OK,
    operation_id='getLastMessages',
    summary='Get unique last messages',
    description='Get unique last messages'
    'for current user',
)
async def get_last_messages(
    current_user: User = Depends(get_current_user),
    message_service: MessageService = Depends(MessageService),
    limit: int = Query(default=100),
    offset: int = Query(default=0),
):
    messages = await message_service.get_unique_last_messages(
        user_id=current_user.id,
        ordering=['-created_at'],
        join=['sender'],
        limit=limit,
        offset=offset,
    )
    return messages

