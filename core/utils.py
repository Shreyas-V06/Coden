import secrets

CHARACTER_SET = "abcdefghjkmnopqrstuvwxyz23456789"
UID_SHORT_LENGTH = 6
UID_LONG_LENGTH = 10

def generate_room_id() -> str:
    return "".join(secrets.choice(CHARACTER_SET) for _ in range(UID_SHORT_LENGTH))
def generate_user_id() -> str:
    return "usr".join(secrets.choice(CHARACTER_SET) for _ in range(UID_LONG_LENGTH))
def generate_question_id() -> str:
    return "qsn".join(secrets.choice(CHARACTER_SET) for _ in range(UID_SHORT_LENGTH))



