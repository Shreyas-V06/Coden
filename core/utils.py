import os
import datetime
import secrets
import jwt
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

CHARACTER_SET = "abcdefghjkmnopqrstuvwxyz23456789"
UID_SHORT_LENGTH = 6
UID_LONG_LENGTH = 10

def generate_room_id() -> str:
    return "".join(secrets.choice(CHARACTER_SET) for _ in range(UID_SHORT_LENGTH))
def generate_user_id() -> str:
    return "usr".join(secrets.choice(CHARACTER_SET) for _ in range(UID_LONG_LENGTH))
def generate_question_id() -> str:
    return "qsn".join(secrets.choice(CHARACTER_SET) for _ in range(UID_SHORT_LENGTH))

def generate_jwt_token(player_id: str, room_id: str, expires_in_hours: int = 1) -> str:
    payload = {
        "player_id": player_id,
        "room_id": room_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=expires_in_hours),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token
