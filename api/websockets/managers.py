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
        # BUG FIX: removed unused `room_id` param that was in the original signature
        if websocket is None or self.active_connections.get(player_id) == websocket:
            self.active_connections.pop(player_id, None)

    def has_active_connections(self, player_id: str) -> bool:
        # BUG FIX: original used bare `player_id` which was out-of-scope; now takes it as param
        return player_id in self.active_connections

    async def notify(
        self,
        player1_id: str,
        player2_id: str,
        room_id: str,
        player1_token: str,
        player2_token: str,
    ):
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


class GameManager:
    def __init__(self):
        self.connections: dict[str, dict[str, WebSocket]] = {}

    async def connect(self, player_id: str, room_id: str, websocket: WebSocket):
        await websocket.accept()
        if room_id not in self.connections:
            self.connections[room_id] = {}
        old_ws = self.connections[room_id].get(player_id)
        self.connections[room_id][player_id] = websocket

        if old_ws and old_ws != websocket:
            try:
                notification = {
                    "status": "error",
                    "message": "You have joined the game from a different connection",
                }
                await old_ws.send_json(data=notification)
                await old_ws.close(
                    code=status.WS_1008_POLICY_VIOLATION,
                    reason="You have joined the game from a different connection",
                )
            except Exception:
                pass

    def disconnect(self, player_id: str, room_id: str, websocket: WebSocket | None = None):
        room = self.connections.get(room_id)
        if room is None:
            return

        stored_ws = room.get(player_id)
        if stored_ws is None:
            return

        if websocket is None or stored_ws == websocket:
            room.pop(player_id, None)
            if not room:
                self.connections.pop(room_id, None)

    def is_room_exists(self, room_id: str) -> bool:
        return room_id in self.connections and bool(self.connections[room_id])

    def is_player_in_room(self, player_id: str, room_id: str) -> bool:
        room = self.connections.get(room_id)
        if room is None:
            return False
        return player_id in room

    async def notify_room(
        self,
        room_id: str,
        message:dict
    ):
       
        room = self.connections.get(room_id)
        if not room:
            return
    
        for pid, ws in list(room.items()):
            try:
                await ws.send_json(data=message)
            except Exception:
                self.disconnect(player_id=pid, room_id=room_id, websocket=ws)

    async def notify_player(self, player_id: str, room_id: str, message: dict):
     
        room = self.connections.get(room_id)
        if not room:
            return

        ws = room.get(player_id)
        if ws is None:
            return

        try:
            await ws.send_json(data=message)
        except Exception:
            self.disconnect(player_id=player_id, room_id=room_id, websocket=ws)


game_manager = GameManager()