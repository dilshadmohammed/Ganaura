# websocket_handler.py
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict
from utils import JWTUtils

active_connections: Dict[str, WebSocket] = {}

async def websocket_endpoint(websocket: WebSocket):
    token = websocket.query_params.get("token")
    user_id = JWTUtils.fetch_user_id_ws(token)
    if not user_id:
        await websocket.close(code=4001)
        return

    await websocket.accept()
    active_connections[user_id] = websocket
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.pop(user_id, None)