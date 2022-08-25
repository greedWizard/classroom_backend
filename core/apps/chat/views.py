from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    WebSocket,
)

from dependency_injector.wiring import (
    inject,
    Provide,
)
from starlette import status

from core.apps.chat.containers import ChatContainer
from core.apps.chat.managers import ChatManager
from core.apps.chat.schemas import (
    DialogDetailSchema,
    DialogStartSchema,
)
from core.apps.chat.services.dialog_service import DialogService
from core.apps.users.dependencies import get_current_user
from core.apps.users.models import User


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
    pass


@router.post(
    '/start-tet-a-tet',
    response_model=DialogDetailSchema,
    status_code=status.HTTP_201_CREATED,
    operation_id='startDialogWithTeacher',
    summary='Start a new private dialog',
    description='Creates a dialog with participants.'
                    'If a dialog already exists between'
                        "participants then it won't be created",
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


# TODO: тесты на эту вьюху
# @router.get(
#     '/my-dialogs',
#     response_model=list[MessageListItemSchema],
#     operation_id='myDialogs',
# )
# async def my_dialogs(
#     user: User = Depends(get_current_user),
# ):
#     message_service = MessageService(user)
#     messages = await message_service.fetch_last()

#     return [MessageListItemSchema.from_orm(message) for message in messages]
