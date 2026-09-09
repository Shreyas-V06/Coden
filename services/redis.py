import redis.asyncio as redis
import json
import time
from fastapi import HTTPException, status

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

metadata_key = "coden:queue:metadata"
queue_key = "coden:queue"
rooms_key = "coden:rooms"

async def addPlayer(player_id:str,player_score:float):
    timestamp = int(time.time())
    player_metadata = {player_id:timestamp}
    async with await r.pipeline(transaction=True) as pipe:
        pipe.zadd(name=metadata_key, mapping=player_metadata)
        pipe.zadd(name=queue_key, mapping={player_id: player_score})
        await pipe.execute()

async def removePlayer(player_id:str):
    async with await  r.pipeline(transaction=True) as pipe:
        pipe.zrem(queue_key,player_id)
        pipe.zrem(metadata_key,player_id)
        await pipe.execute()

async def addRoom(roomid: str, player1_id: str, player2_id: str, question_ids: list[str], status_value: str = "EMPTY"):
    room = {
        "roomid": roomid,
        "player1_id": player1_id,
        "player2_id": player2_id,
        "question_ids": question_ids,
        "status": status_value,
    }
    async with await r.pipeline(transaction=True) as pipe:
        pipe.hset(name=rooms_key, key=roomid, value=json.dumps(obj=room))
        await pipe.execute()


async def updateRoomStatus(roomid: str, new_status: str):
    while True:
        try:
            await r.watch(rooms_key)
            raw_room = await r.hget(name=rooms_key, key=roomid)
            if not raw_room:
                await r.unwatch()
                return False
            room = json.loads(s=raw_room)
            room["status"] = new_status
            async with await r.pipeline(transaction=True) as pipe:
                pipe.hset(name=rooms_key, key=roomid, value=json.dumps(obj=room))
                await pipe.execute()
            return True
        except redis.WatchError:
            continue

async def removeRoom(roomid: str):
    async with await r.pipeline(transaction=True) as pipe:
        pipe.hdel(rooms_key, roomid)
        await pipe.execute()



    
    
