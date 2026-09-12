import asyncio
import json
from api.websockets.managers import manager,gm
from fastapi import WebSocket,APIRouter,HTTPException,status
from core.utils import decode_jwt_token
from services.redis import addPlayer,removePlayer

router = APIRouter()

HEARTBEAT_INTERVAL: float = 10.0
HEARTBEAT_TIMEOUT: float = 5.0


@router.websocket(path="/matchmaking")
async def join_matchmaking(websocket: WebSocket, player_id: str, score: float):
    await manager.connect(player_id=player_id, websocket=websocket)
    pong_event = asyncio.Event()

    async def heartbeat():
        while True:
            await asyncio.sleep(delay=HEARTBEAT_INTERVAL)
            pong_event.clear()
            try:
                await websocket.send_json(data={"type": "ping"})
                await asyncio.wait_for(fut=pong_event.wait(), timeout=HEARTBEAT_TIMEOUT)
            except asyncio.TimeoutError:
                await websocket.close(
                    code=status.WS_1008_POLICY_VIOLATION,
                    reason="Heartbeat timeout",
                )
                break
            except Exception:
                break

    heartbeat_task = asyncio.create_task(coro=heartbeat())
    try:
        await addPlayer(player_id=player_id, player_score=score)
        while True:
            message = await websocket.receive_text()
            if message == "pong":
                pong_event.set()
                continue
            try:
                parsed = json.loads(s=message)
                if isinstance(parsed, dict) and parsed.get("type") == "pong":
                    pong_event.set()
                    continue
            except Exception:
                pass
    except:
        manager.disconnect(player_id=player_id, websocket=websocket)
        if not manager.has_active_connections(player_id=player_id):
            await removePlayer(player_id=player_id)
    finally:
        heartbeat_task.cancel()


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
    