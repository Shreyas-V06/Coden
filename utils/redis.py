import redis.asyncio as redis
import json
import time
from fastapi import HTTPException, status
from utils.general import generate_room_id
from utils.problem import get_problems_by_difficulty

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

metadata_key = "coden:queue:metadata"
queue_key = "coden:queue"
rooms_key_prefix = "coden:rooms"
ROOM_STATUS_EMPTY = "EMPTY"

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

async def clearMatchmakingQueue():
    await r.delete(queue_key, metadata_key)


async def createRoom(player1_id: str, player2_id: str) -> dict:
 
    room_id = generate_room_id()
    problem_ids = await get_problems_by_difficulty()

    difficulties = ["easy", "medium", "hard", "expert"]
    problems = [
        {
            "problem_id": problem_ids[i],
            "difficulty": difficulties[i],
            player1_id: False,
            player2_id: False,
        }
        for i in range(len(difficulties))
    ]

 
    room_data = {
        "room_id": room_id,
        "status": ROOM_STATUS_EMPTY,
        "player1": player1_id,
        "player2": player2_id,
        "ends_at": 0,          
        "scores": {
            player1_id: 0,
            player2_id: 0,
        },
        "problems": problems,
        "messages": {},
    }


    redis_key = f"{rooms_key_prefix}:{room_id}"
    await r.set(redis_key, json.dumps(room_data))


    return {
        "room_id": room_id,
        "player1_id": player1_id,
        "player2_id": player2_id,
    }
