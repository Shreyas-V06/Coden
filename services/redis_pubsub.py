import redis.asyncio as redis
import json 

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

async def listen_to_matches():
    pubsub = r.pubsub()
    await pubsub.subscribe("coden:matches")

    async for message in pubsub.listen():
        if message['type']=='message':
            raw_data = message['data']
            parsed_data = json.loads(raw_data)
            print("Match Recieved : ",parsed_data)
            player1_id = parsed_data['player1_id']
            player2_id = parsed_data['player2_id']
            
            #create a room 
            #notify the roomids to players

async def publish_match(matchup:dict):
    payload = json.dumps(matchup)
    print("Match published : ",payload)
    await r.publish("coden:matches",payload)
