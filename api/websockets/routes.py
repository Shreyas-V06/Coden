from api.websockets.managers import manager,gm
from fastapi import WebSocket,APIRouter,HTTPException,status
from core.utils import decode_jwt_token
from services.redis import addPlayer,removePlayer

router = APIRouter()


@router.websocket(path="/matchmaking")
async def join_matchmaking(websocket: WebSocket, player_id: str, score: float):
    await manager.connect(player_id=player_id, websocket=websocket)
    try:
        await addPlayer(player_id=player_id, player_score=score)
        while True:
            await websocket.receive_text()
    except:
        manager.disconnect(player_id=player_id, websocket=websocket)
        if not manager.has_active_connections(player_id=player_id):
            await removePlayer(player_id=player_id)


@router.websocket(path="/rooms/{room_id}")
async def join_room(websocket: WebSocket,room_id:str,player_token:str):
     payload = decode_jwt_token(token=player_token)
     if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
     start_game = await gm.connect(room_id=room_id, player_id=payload['player_id'], websocket=websocket)
     
     if start_game:
         #trigger_start
         pass
     else:
        #trigger_background_loop
        pass
    