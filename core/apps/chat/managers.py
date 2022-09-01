from fastapi import WebSocket

from core.apps.chat.models import Message
from core.apps.chat.schemas import MessageDetailSchema


class BroadcastMixin:
    @staticmethod
    async def broadcast(websocket: WebSocket, message: Message):
        message_schema = MessageDetailSchema.from_orm(message)
        await websocket.send_json(message_schema.dict())

    async def broadcast_batch(
        self,
        messages: list[Message],
        websocket: WebSocket,
    ):
        for message in messages:
            await self.broadcast(websocket, message)


class ChatManager(BroadcastMixin):
    def __init__(self):
        self.active_connections: dict[str, set[WebSocket]] = {}

    async def add_connection(self, dialog_id: int, websocket: WebSocket):
        await websocket.accept()

        if dialog_id not in self.active_connections.keys():
            self.active_connections[dialog_id] = {websocket}
        else:
            self.active_connections[dialog_id].add(websocket)

    async def remove_connection(self, dialog_id: int, websocket: WebSocket) -> WebSocket:
        try:
            self.active_connections[dialog_id].remove(websocket)
        except (KeyError, ValueError):
            pass

    async def broadcast_message_to_all_participants(self, message: Message):
        for websocket in self.active_connections[message.dialog_id]:
            await self.broadcast(websocket, message)
