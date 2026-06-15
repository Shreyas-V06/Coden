from services.redis_queue import r,removePlayer
import asyncio
import time

#TODO: Wrap it in redis pipeline 

def calculateDelta(player_timestamp:int):
    waitingTime = int(time.time())-player_timestamp
    return 20+(waitingTime*3)

async def matchmake():
    key1="coden:queue:metadata"
    key2="coden:queue"

    c = await r.zrange(key1,0,0,withscores=True)

    if c:
        c_id = c[0][0]
        c_time = c[0][1]
    else:
        return False

    c_delta = calculateDelta(c_time)
    c_score_raw = await r.zscore(key2,c_id)


    if(c_score_raw is None):
        await removePlayer(c_id)
        return True
    c_score = int(c_score_raw)

    lowerbound = c_score - c_delta
    upperbound = c_score + c_delta

    search_pool = await r.zrange(key2,lowerbound,upperbound,byscore=True,withscores=False)
    opponent_id = ""

    for user in search_pool:
        if(user!=c_id):
            opponent_id=user
            break
    
    if(opponent_id!=""):       
        matchup = {c_id:opponent_id}
        await asyncio.gather(removePlayer(c_id),removePlayer(opponent_id))

        #TODO: create room and send websocket response 

        return True

    return False

async def matchmaker():
    while(True):
        matched = await matchmake()

        if not matched:
            await asyncio.sleep(1)
        else:
            await asyncio.sleep(0.01)




    






