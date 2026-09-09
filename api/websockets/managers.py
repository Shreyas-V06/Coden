from fastapi import WebSocket
from services.redis import updateRoomStatus

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
                self.disconnect(player_id=player1_id)                
        if ws2:
            try:
                await ws2.send_json(data=notification_p2)
            except Exception:
                self.disconnect(player_id=player2_id)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            try:
                await connection.send_text(data=message)
            except Exception:
                pass


class GameManager:
    def __init__(self):
        self.active_connections: dict = {}

    async def connect(self, room_id: str, player_id: str, websocket: WebSocket) -> bool:
        await websocket.accept()
        if room_id not in self.active_connections:
            self.active_connections[room_id] = {}
        self.active_connections[room_id][player_id] = websocket
        
        connection_count = len(self.active_connections[room_id])
        trigger_start = False

        if connection_count == 1:
            await updateRoomStatus(roomid=room_id, new_status="WAITING")
        elif connection_count == 2:
            await updateRoomStatus(roomid=room_id, new_status="LIVE")
            trigger_start = True

        return trigger_start

    async def disconnect(self,room_id:str,player_id:str):
        if room_id not in self.active_connections:
            return
        self.active_connections[room_id].pop(player_id, None)
        if len(self.active_connections[room_id]) == 0:
                del self.active_connections[room_id]

    async def broadcast_to_room(self,room_id:str,payload:dict):
        room_connections = list(self.active_connections.get(room_id, {}).items())

        for player_id, websocket in room_connections:
            try:
                await websocket.send_json(data=payload)
            except Exception:
                await self.disconnect(room_id=room_id, player_id=player_id)


manager = ConnectionManager()
gm = GameManager()
