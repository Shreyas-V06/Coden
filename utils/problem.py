from models.domain import Problem
from core.database import get_db
from utils.general import generate_problem_id
from fastapi import HTTPException, status


DIFFICULTY_ORDER = ["easy", "medium", "hard", "expert"]


async def get_problems_by_difficulty() -> list[str]:
    db = get_db()
    problem_ids: list[str] = []

    for difficulty in DIFFICULTY_ORDER:
        pipeline = [
            {"$match": {"difficulty": difficulty}},
            {"$project": {"_id": 0, "problem_id": 1}},
            {"$limit": 1},
        ]
        problems = await db.problems.aggregate(pipeline=pipeline).to_list(length=1)

        if not problems:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Problem not found for difficulty level: {difficulty}."
            )

        problem_ids.append(problems[0]["problem_id"])

    return problem_ids




