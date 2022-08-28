from fastapi import WebSocket

from core.apps.chat.models import Message
from core.apps.chat.schemas import MessageDetailSchema


class ChatManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def add_connection(self, dialog_id: int, websocket: WebSocket):
        await websocket.accept()
        if dialog_id not in self.active_connections.keys():
            self.active_connections[dialog_id] = [websocket]
        else:
            self.active_connections[dialog_id].append(websocket)

    async def remove_connection(self, dialog_id: int, websocket: WebSocket) -> WebSocket:
        try:
            self.active_connections[dialog_id].remove(websocket)
        except (KeyError, ValueError):
            pass

    @staticmethod
    async def broadcast(websocket: WebSocket, message: Message):
        message_schema = MessageDetailSchema.from_orm(message)
        await websocket.send_json(message_schema.dict())

    async def broadcast_message_to_all_participants(self, message: Message):
        for websocket in self.active_connections[message.dialog_id]:
            await self.broadcast(websocket, message)

    async def broadcast_batch(
        self,
        messages: list[Message],
        websocket: WebSocket,
    ):
        messages_models = [MessageDetailSchema.from_orm(message) for message in messages]
        await websocket.send_json(
            data=[message_model.dict() for message_model in messages_models],
        )
