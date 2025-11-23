# sockets/dashboard_ws.py

import json
from fastapi import APIRouter, WebSocket
from sockets.manager import ConnectionManager

router = APIRouter()
manager = ConnectionManager()


@router.websocket("/ws/dashboard")
async def dashboard_ws(websocket: WebSocket):
    await manager.connect_dashboard(websocket)

    try:
        while True:
            await websocket.receive_text()   # dashboards don't send anything for now
    except Exception:
        await manager.disconnect_dashboard(websocket)
