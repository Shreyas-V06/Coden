from pydantic import BaseModel, EmailStr
from typing import List, Literal, Optional

class User(BaseModel):
    username: str
    email: EmailStr
    user_id: str
    score: float

class Problem(BaseModel):
    problem_id: Optional[str] = None
    problem_statement: str
    difficulty: Literal["easy", "medium", "hard", "expert"]
    testcase_input: List[str]
    testcase_output: List[str]
    weight: float




    


