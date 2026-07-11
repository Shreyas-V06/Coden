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
        pipe.zadd(metadata_key,player_metadata)
        pipe.zadd(queue_key,{player_id:player_score})
        await pipe.execute()

async def removePlayer(player_id:str):
    async with await  r.pipeline(transaction=True) as pipe:
        pipe.zrem(queue_key,player_id)
        pipe.zrem(metadata_key,player_id)
        await pipe.execute()

async def addRoom(roomid: str, player1_id: str, player2_id: str, question_ids: list[str], status_value: str = "empty"):
    room = {
        "roomid": roomid,
        "player1_id": player1_id,
        "player2_id": player2_id,
        "question_ids": question_ids,
        "status": status_value,
    }
    await r.hset(rooms_key, roomid, json.dumps(room))


    
    
    
