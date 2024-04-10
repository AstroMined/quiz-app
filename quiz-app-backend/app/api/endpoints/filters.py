# filename: app/api/endpoints/filters.py

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import QuestionSchema, FilterParamsSchema
from app.crud import filter_questions

router = APIRouter()

@router.get("/questions/filter", response_model=List[QuestionSchema])
def filter_questions_endpoint(
    filters: FilterParamsSchema = Depends(),
    db: Session = Depends(get_db)
):
    filtered_questions = filter_questions(
        db=db,
        subject=filters.subject,
        topic=filters.topic,
        subtopic=filters.subtopic,
        difficulty=filters.difficulty,
        tags=filters.tags
    )

    if filtered_questions is None:
        return []
    return filtered_questions
