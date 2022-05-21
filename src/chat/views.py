from fastapi import APIRouter, Query, WebSocket

from user.dependencies import websocket_user

router = APIRouter(tags=['chat'])


@router.websocket('/',)
async def websocket_endpoint(
    websocket: WebSocket,
    jwt_token=Query(...),
):
    await websocket.accept()
    user = await websocket_user(token=jwt_token)
    print(user)
    while True:
        data = await websocket.receive_json()
        await websocket.send_json(data)
    await websocket.close()