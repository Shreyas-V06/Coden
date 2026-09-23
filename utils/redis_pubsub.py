import redis.asyncio as redis
import json 
from api.websockets.managers import manager
from utils.redis import createRoom
from utils.general import generate_jwt_token

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

async def listen_to_matches():
    pubsub = r.pubsub()
    await pubsub.subscribe("coden:matches")

    async for message in pubsub.listen():
        if message["type"] != "message":
            continue
        try:
            raw_data = message["data"]
            parsed_data = json.loads(s=raw_data)
            player1_id = parsed_data["player1_id"]
            player2_id = parsed_data["player2_id"]

            
            room_details = await createRoom(player1_id=player1_id, player2_id=player2_id)
            print("Match Recieved")
            await manager.notify(
                player1_id=player1_id,
                player2_id=player2_id,
                room_id=room_details["room_id"],
                player1_token=generate_jwt_token({"room_id":room_details["room_id"],"player_id":player1_id}),
                player2_token=generate_jwt_token({"room_id":room_details["room_id"],"player_id":player2_id}),
            )
            
        except Exception as exc:
            print("listen_to_matches error:", exc)

async def publish_match(matchup:dict):
    payload = json.dumps(obj=matchup)
    print("Match published : ",payload)
    await r.publish(channel="coden:matches", message=payload)


