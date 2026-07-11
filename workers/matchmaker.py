from services.redis import r,metadata_key,queue_key
from services.redis_pubsub import publish_match
import asyncio
import time


MATCHMAKING_LUA_SCRIPT = """
local metadata_key = KEYS[1]
local queue_key = KEYS[2]
local current_time = tonumber(ARGV[1])
local batch_size = tonumber(ARGV[2])

local candidates = redis.call('ZRANGE',metadata_key,0,batch_size-1,'WITHSCORES')
if #candidates>0 then
    for i=1,#candidates,2 do
        local cid = candidates[i]
        local ctime = tonumber(candidates[i+1])
        local cscore_raw = redis.call('ZSCORE',queue_key,cid)
        if not cscore_raw then
            redis.call('ZREM',metadata_key,cid)
            redis.call('ZREM',queue_key,cid)
        else
            local cscore = tonumber(cscore_raw)
            local wait_time = current_time - ctime
            local delta = 20 + (3*wait_time)
            local lb = cscore-delta
            local ub = cscore+delta
            local search_pool = redis.call('ZRANGEBYSCORE',queue_key,lb,ub)
            for j=1,#search_pool do
                local opp_id = search_pool[j]
                if opp_id ~= cid then
                    redis.call('ZREM',metadata_key,cid)
                    redis.call('ZREM',queue_key,cid)
                    redis.call('ZREM',metadata_key,opp_id)
                    redis.call('ZREM',queue_key,opp_id)
                    return {cid,opp_id}
                end
            end
        end
    end
end

return {}
"""

matchmaker_script = r.register_script(MATCHMAKING_LUA_SCRIPT)


async def matchmake():
    current_time = int(time.time())
    batch_size = 10

    matchup = await matchmaker_script([metadata_key,queue_key],[current_time,batch_size])

    if matchup: 
        await publish_match({"player1_id":matchup[0],"player2_id":matchup[1]})
        return True
    
    return False

async def matchmaker():
    while(True):
        matched = await matchmake()
        if not matched:
            await asyncio.sleep(1)
        else:
            await asyncio.sleep(0.01)




    






