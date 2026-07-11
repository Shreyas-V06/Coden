from api.websockets.manager import manager
from fastapi import WebSocket,APIRouter
from services.redis import addPlayer,removePlayer
router = APIRouter()


@router.websocket("/matchmaking")
async def join_matchmaking(websocket: WebSocket, player_id: str, score: float):
    await manager.connect(player_id,websocket)
    try:
        await addPlayer(player_id,score)
        while True:
                await websocket.receive_text()
    except:
         manager.disconnect(player_id)
         await removePlayer(player_id)


