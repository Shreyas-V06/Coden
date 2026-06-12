import redis.asyncio as redis
from models.domain import User
import time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

async def addPlayerMetadata(player:User):
    key = "coden:queue:metadata"
    player_id = player.user_id
    timestamp = int(time.time())
    await r.hset(key,player_id,timestamp)

async def addPlayerToQueue(player:User):
    key = "coden:queue"
    player_id = player.user_id
    player_score = player.score
    await r.zadd(key,{player_id:player_score})
    await addPlayerMetadata(player)

    
    
    
