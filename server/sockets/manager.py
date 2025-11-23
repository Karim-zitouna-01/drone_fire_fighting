# sockets/manager.py

class ConnectionManager:
    def __init__(self):
        self.drones = {}         # drone_id -> websocket
        self.dashboards = set()  # list of dashboard websockets

    async def connect_drone(self, drone_id: str, websocket):
        self.drones[drone_id] = websocket
        await websocket.accept()

    async def disconnect_drone(self, drone_id: str):
        if drone_id in self.drones:
            del self.drones[drone_id]

    async def connect_dashboard(self, websocket):
        self.dashboards.add(websocket)
        await websocket.accept()

    async def disconnect_dashboard(self, websocket):
        if websocket in self.dashboards:
            self.dashboards.remove(websocket)

    # BROADCAST to all dashboards
    async def broadcast_to_dashboards(self, message: dict):
        import json
        data = json.dumps(message)
        for ws in list(self.dashboards):
            try:
                await ws.send_text(data)
            except:
                self.dashboards.remove(ws)

    # SEND to a specific drone
    async def send_to_drone(self, drone_id: str, message: dict):
        if drone_id in self.drones:
            import json
            await self.drones[drone_id].send_text(json.dumps(message))
