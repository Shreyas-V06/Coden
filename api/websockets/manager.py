from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, player_id:str, websocket: WebSocket):
        await websocket.accept()
        connection = {player_id:websocket}
        self.active_connections[player_id]=connection

    def disconnect(self, player_id:str):
        self.active_connections.pop(player_id)

    async def notify(self,player1_id:str,player2_id:str,room_id:str):

        ws1 = self.active_connections.get(player1_id)
        ws2 = self.active_connections.get(player2_id)
    
        notification = {
            "status": "success",
            "player1_id": player1_id,
            "player2_id": player2_id,
            "room_id": room_id
        }
        if ws1:
            try:
                await ws1.send_json(notification)
            except Exception:
                self.disconnect(player1_id)
                
        if ws2:
            try:
                await ws2.send_json(notification)
            except Exception:
                self.disconnect(player2_id)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()