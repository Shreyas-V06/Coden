from core.utils import generate_room_id,generate_jwt_token
from services.redis import addRoom
from services.questions import generate_question_id

async def createRoom(player1_id,player2_id):
    room_id = generate_room_id()
    question_ids = generate_question_id()
    await addRoom(room_id,player1_id,player2_id,question_ids)
    player1_token = generate_jwt_token(player1_id,room_id,1)
    player2_token = generate_jwt_token(player2_id,room_id,1)
    return {"player1_token":player1_token,"player2_token":player2_token,"room_id":room_id}


    