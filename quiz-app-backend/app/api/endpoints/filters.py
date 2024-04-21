# filename: app/api/endpoints/filters.py

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import QuestionSchema, FilterParamsSchema
from app.crud import filter_questions, get_questions_crud

router = APIRouter()

@router.get("/questions/filter", response_model=List[QuestionSchema])
def filter_questions_endpoint(
    filters: FilterParamsSchema = Depends(),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    if not any(filter_value for filter_value in filters.model_dump().values()):
        questions = get_questions_crud(db=db, skip=skip, limit=limit)
        return questions
    else:
        filtered_questions = filter_questions(db=db, filters=filters, skip=skip, limit=limit)
        return filtered_questions
