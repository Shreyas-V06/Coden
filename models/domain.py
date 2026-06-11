from pydantic import BaseModel,EmailStr
from typing import List,Literal

class User(BaseModel):
    username:str
    email:EmailStr
    user_id:str
    score:float

class Question(BaseModel):
    question_id:str
    problem_statement:str
    testcase_input: List[str]
    testcase_output: List[str]
    weight:float

class Submission(BaseModel):
    question_id:str
    language:Literal["java","cpp","python"]
    code:str
    user_id:str
    submission_time:int

class Response(BaseModel):
    question_id:str
    delta:float
    is_solved:bool
    user_id:str
    penalty:int
    evaluation_time:int
    evaluation_space:int
    verdict:str
    


