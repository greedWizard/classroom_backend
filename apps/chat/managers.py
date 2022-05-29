from typing import (
    Any,
    List,
    NewType,
)

from fastapi import WebSocket

from apps.chat.models import Dialog
from apps.chat.schemas import MessageSchema
from common.utils import prepare_json_list


ws_connection = NewType('WsConnection', list[dict[str, Any]])


class ChatManager:
    # TODO: поменять на нормальный DI через провайдеры контейнера
    def __init__(self):
        self.active_connections: List[ws_connection] = []

    def _get_dialog_connections(self, dialog: Dialog) -> list[ws_connection]:
        return [
            connection
            for connection in self.active_connections
            if connection['dialog'].id == dialog.id
        ]

    @staticmethod
    def _get_connection(websocket: WebSocket, dialog: Dialog) -> ws_connection:
        return {'websocket': websocket, 'dialog': dialog}

    async def connect(self, websocket: WebSocket, dialog: Dialog):
        await websocket.accept()
        self.active_connections.append(self._get_connection(websocket, dialog))

    async def disconnect(self, websocket: WebSocket, dialog: Dialog):
        self.active_connections.remove(self._get_connection(websocket, dialog))

    async def broadcast(self, messages: list[MessageSchema], dialog: Dialog):
        dialog_connections = self._get_dialog_connections(dialog)

        for connection in dialog_connections:
            await connection['websocket'].send_json(prepare_json_list(messages))

    async def remove_inactive(self):
        self.active_connections = [
            connection
            for connection in self.active_connections
            if connection['websocket']
        ]
