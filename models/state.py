from pydantic import BaseModel
from typing import List
from domain import Response

class Room(BaseModel):
    room_id:str
    question_ids:List[str]
    player1_id:str
    player2_id:str
    time:int
    player1_score:float
    player1_submissions:List[Response]
    player2_score:float
    player2_submissions:List[Response]


