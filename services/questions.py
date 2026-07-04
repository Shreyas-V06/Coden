from models.domain import Question
from core.database import get_db
from core.utils import generate_question_id
from fastapi import HTTPException, status


async def create_question(question_in:Question)->dict:
    db = get_db()
    document = question_in.model_dump()
    document['question_id']=generate_question_id()
    result = await db.questions.insert_one(document)
    if not result.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to insert question into the database."
        )
    return {"status":"success","message":"question created successfully."}


async def delete_question(question_id: str) -> dict:
    db = get_db()
    result = await db.questions.delete_one({"question_id": question_id})

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found."
        )

    return {"status": "success", "message": "question deleted successfully."}


async def update_question(question_id: str, question_data: dict) -> dict:
    db = get_db()
    updates = {key: value for key, value in question_data.items() if key != "question_id"}

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No update data provided."
        )
    result = await db.questions.update_one(
        {"question_id": question_id},
        {"$set": updates}
    )
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found."
        )
    return {"status": "success", "message": "question updated successfully."}
  
