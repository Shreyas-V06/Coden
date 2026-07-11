import redis.asyncio as redis
import json 
from api.websockets.manager import manager
from services.room import createRoom

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

async def listen_to_matches():
    pubsub = r.pubsub()
    await pubsub.subscribe("coden:matches")

    async for message in pubsub.listen():
        if message["type"] != "message":
            continue
        try:
            raw_data = message["data"]
            parsed_data = json.loads(raw_data)
            player1_id = parsed_data["player1_id"]
            player2_id = parsed_data["player2_id"]
            room_details = await createRoom(player1_id, player2_id)
            print("Match Recieved: ", room_details)
            await manager.notify(
                player1_id,
                player2_id,
                room_details["room_id"],
                room_details["player1_token"],
                room_details["player2_token"],
            )
        except Exception as exc:
            print("listen_to_matches error:", exc)

async def publish_match(matchup:dict):
    payload = json.dumps(matchup)
    print("Match published : ",payload)
    await r.publish("coden:matches",payload)
