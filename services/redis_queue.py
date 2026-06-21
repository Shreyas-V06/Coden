import redis.asyncio as redis
import time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

metadata_key = "coden:queue:metadata"
queue_key = "coden:queue"

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



    
    
    
