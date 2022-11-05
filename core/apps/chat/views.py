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
    LastMessageDetail,
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
    limit: int = Query(50),
    chat_manager: ChatManager = Depends(Provide[ChatContainer.manager]),
    dialog_repository: DialogRepository = Depends(DialogRepository),
    message_service: MessageService = Depends(MessageService),
):
    user = await get_websocket_user(token=jwt_token)
    await chat_manager.add_connection(dialog_id, websocket)

    if not await dialog_repository.check_participant_in_dialog(user.id, dialog_id):
        await websocket.close()
        raise WebSocketDisconnect(403)

    message_joins = ['sender']

    previous_messages, _ = await message_service.fetch(
        _ordering=['created_at'],
        join=message_joins,
        dialog_id=dialog_id,
        limit=limit,
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
            message, _ = await message_service.create(
                message_create_schema,
                join=message_joins,
            )
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
        await websocket.receive_json()
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
    response_model=list[LastMessageDetail],
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
        join=['sender', 'dialog', 'dialog.participants'],
        limit=limit,
        offset=offset,
    )
    return messages


@router.get(
    '/dialogs/{dialog_id}',
    response_model=DialogDetailSchema,
    status_code=status.HTTP_200_OK,
    operation_id='getDialogDetail',
    summary='Get dialog info with participants',
    description='Get dialog info with participants',
)
async def get_dialog_detail(
    dialog_id: int,
    current_user: User = Depends(get_current_user),
    dialog_service: DialogService = Depends(DialogService),
):
    dialog_joins = ['participants', 'author']

    dialog, _ = await dialog_service.retrieve_participating_dialog(
        dialog_id=dialog_id,
        retriever_id=current_user.id,
        _join=dialog_joins,
    )
    if not dialog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'dialog_id': 'Not found'})
    return dialog


@router.get(
    '/messages',
    response_model=list[MessageDetailSchema],
    status_code=status.HTTP_200_OK,
    operation_id='getMessages',
    summary='Get chat messages from dialog',
    description='Get chat messages by dialog id',
)
async def get_dialog_detail(
    dialog_id: int = Query(...),
    current_user: User = Depends(get_current_user),
    message_service: MessageService = Depends(MessageService),
    limit: int = Query(default=100),
    offset: int = Query(default=0),
):
    messages, _ = await message_service.fetch_by_dialog_id(
        dialog_id=dialog_id,
        _ordering=['-created_at'],
        user_id=current_user.id,
        join=['sender'],
        limit=limit,
        offset=offset,
    )

    if not messages:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={'dialog_id': 'Not found'})
    return messages[::-1]

