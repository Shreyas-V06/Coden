from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import bcrypt

from core.database import get_db
from models.domain import User, Problem
from utils.general import generate_user_id,generate_problem_id,generate_jwt_token,decode_jwt_token


router = APIRouter(prefix="/api", tags=["HTTP"])



class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class ProblemRequest(BaseModel):
    problem_statement: str
    difficulty: str
    testcase_input: List[str]
    testcase_output: List[str]
    weight: float


class EditProblemRequest(BaseModel):
    problem_statement: Optional[str] = None
    difficulty: Optional[str] = None
    testcase_input: Optional[List[str]] = None
    testcase_output: Optional[List[str]] = None
    weight: Optional[float] = None


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(body: RegisterRequest):
    db = get_db()

    if await db["users"].find_one({"username": body.username}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken.",
        )
    if await db["users"].find_one({"email": body.email}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered.",
        )

    user_id = generate_user_id()

    user = User(
        username=body.username,
        email=body.email,
        user_id=user_id,
        score=0.0,
    )

    hashed_pw = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()

    doc = user.model_dump()
    doc["password"] = hashed_pw

    await db["users"].insert_one(doc)

    return {
        "success": True,
        "response": "User registered successfully.",
        "user_id": user_id,
    }



@router.post("/login", status_code=status.HTTP_200_OK)
async def login(body: LoginRequest):

    db = get_db()

    user_doc = await db["users"].find_one({"username": body.username})

    if not user_doc:
        return {
            "success": False,
            "response": "Username not found.",
        }

    stored_hash: str = user_doc.get("password", "")
    if not bcrypt.checkpw(body.password.encode(), stored_hash.encode()):
        return {
            "success": False,
            "response": "Incorrect password.",
        }

    payload = {"username":user_doc["username"],
                "userid":user_doc["user_id"],
                "score":user_doc.get("score", 0.0)}

    token = generate_jwt_token(payload)

    return {
        "success": True,
        "response": "Logged In",
        "token": token,
    }


@router.post("/problems", status_code=status.HTTP_201_CREATED)
async def add_problem(body: ProblemRequest):
 
    db = get_db()

    problem_id = generate_problem_id()

    problem = Problem(
        problem_id=problem_id,
        problem_statement=body.problem_statement,
        difficulty=body.difficulty,
        testcase_input=body.testcase_input,
        testcase_output=body.testcase_output,
        weight=body.weight,
    )

    doc = problem.model_dump()
    await db["problems"].insert_one(doc)

    return {
        "success": True,
        "response": "Problem added successfully.",
        "problem_id": problem_id,
    }



@router.patch("/problems/{problem_id}", status_code=status.HTTP_200_OK)
async def edit_problem(problem_id: str, body: EditProblemRequest):

    db = get_db()

    existing = await db["problems"].find_one({"problem_id": problem_id})
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Problem with id '{problem_id}' not found.",
        )

    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update.",
        )

    await db["problems"].update_one(
        {"problem_id": problem_id},
        {"$set": updates},
    )

    return {
        "success": True,
        "response": f"Problem '{problem_id}' updated successfully.",
    }



@router.delete("/problems/{problem_id}", status_code=status.HTTP_200_OK)
async def delete_problem(problem_id: str):
    db = get_db()

    result = await db["problems"].delete_one({"problem_id": problem_id})

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Problem with id '{problem_id}' not found.",
        )

    return {
        "success": True,
        "response": f"Problem '{problem_id}' deleted successfully.",
    }




@router.get("/problems/{problem_id}", status_code=status.HTTP_200_OK)
async def get_problem(problem_id: str):
    
    db = get_db()

    doc = await db["problems"].find_one(
        {"problem_id": problem_id},
        {"_id": 0},
    )

    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Problem with id '{problem_id}' not found.",
        )

    return {
        "success": True,
        "problem": doc,
    }
