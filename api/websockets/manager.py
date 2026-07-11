from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, player_id:str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[player_id]=websocket

    def disconnect(self, player_id:str):
        self.active_connections.pop(player_id)

    async def notify(self,player1_id:str,player2_id:str,room_id:str,player1_token:str,player2_token:str):

        ws1 = self.active_connections.get(player1_id)
        ws2 = self.active_connections.get(player2_id)
    
        notification_p1 = {
            "status": "success",
            "token": player1_token,
            "room_id": room_id
        }

        notification_p2 = {
            "status": "success",
            "token": player2_token,
            "room_id": room_id
        }

        if ws1:
            try:
                await ws1.send_json(notification_p1)
            except Exception:
                self.disconnect(player1_id)
                
        if ws2:
            try:
                await ws2.send_json(notification_p2)
            except Exception:
                self.disconnect(player2_id)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()