from models.domain import Problem
from core.database import get_db
from utils.general import generate_problem_id
from fastapi import HTTPException, status


DIFFICULTY_ORDER = ["easy", "medium", "hard", "expert"]


async def create_problem(problem_in: Problem) -> dict:
    db = get_db()
    document = problem_in.model_dump()
    document['problem_id'] = generate_problem_id()
    result = await db.problems.insert_one(document=document)
    if not result.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to insert problem into the database."
        )
    return {"status": "success", "message": "problem created successfully."}


async def delete_problem(problem_id: str) -> dict:
    db = get_db()
    result = await db.problems.delete_one(filter={"problem_id": problem_id})

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found."
        )

    return {"status": "success", "message": "problem deleted successfully."}


async def update_problem(problem_id: str, problem_data: dict) -> dict:
    db = get_db()
    updates = {key: value for key, value in problem_data.items() if key != "problem_id"}

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update data provided."
        )
    result = await db.problems.update_one(
        filter={"problem_id": problem_id},
        update={"$set": updates}
    )
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Problem not found."
        )
    return {"status": "success", "message": "problem updated successfully."}


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


# Backwards compatibility aliases
create_question = create_problem
delete_question = delete_problem
update_question = update_problem
get_questions_by_difficulty = get_problems_by_difficulty

