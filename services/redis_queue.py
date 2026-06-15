import redis.asyncio as redis
from models.domain import User
import time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

#TODO: 
async def addPlayerMetadata(player:User):
    key = "coden:queue:metadata"
    player_id = player.user_id
    timestamp = int(time.time())
    player_metadata = {player_id:timestamp}
    await r.zadd(key,player_metadata)

async def removePlayerMetadata(player_id):
    key = "coden:queue:metadata"
    await r.zrem(key,player_id)

async def addPlayer(player:User):
    key = "coden:queue"
    player_id = player.user_id
    player_score = player.score
    await r.zadd(key,{player_id:player_score})
    await addPlayerMetadata(player)

async def removePlayer(player_id):
    key = "coden:queue"
    await r.zrem(key,player_id)
    await removePlayerMetadata(player_id)



    
    
    
