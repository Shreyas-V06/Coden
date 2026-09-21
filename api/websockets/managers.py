from fastapi import WebSocket, status


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, player_id: str, websocket: WebSocket):
        await websocket.accept()
        old_ws = self.active_connections.get(player_id)
        self.active_connections[player_id] = websocket

        if old_ws and old_ws != websocket:
            try:
                notification = {
                    "status": "error",
                    "message": "You have logged in from a different device",
                }
                await old_ws.send_json(data=notification)
                await old_ws.close(
                    code=status.WS_1008_POLICY_VIOLATION,
                    reason="You have logged in from a different device",
                )
            except Exception:
                pass

    def disconnect(self, player_id: str, websocket: WebSocket | None = None):
        if websocket is None or self.active_connections.get(player_id) == websocket:
            self.active_connections.pop(player_id, None)

    def has_active_connections(self, player_id: str) -> bool:
        return player_id in self.active_connections

    async def notify(self,player1_id:str,player2_id:str,room_id:str,player1_token:str,player2_token:str):

        ws1 = self.active_connections.get(player1_id)
        ws2 = self.active_connections.get(player2_id)
    
        notification_p1 = {
            "status": "success",
            "token": player1_token,
            "room_id": room_id,
        }

        notification_p2 = {
            "status": "success",
            "token": player2_token,
            "room_id": room_id,
        }

        if ws1:
            try:
                await ws1.send_json(data=notification_p1)
            except Exception:
                self.disconnect(player_id=player1_id, websocket=ws1)                
        if ws2:
            try:
                await ws2.send_json(data=notification_p2)
            except Exception:
                self.disconnect(player_id=player2_id, websocket=ws2)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            try:
                await connection.send_text(data=message)
            except Exception:
                pass


manager = ConnectionManager()

