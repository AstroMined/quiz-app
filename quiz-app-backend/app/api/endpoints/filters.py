# filename: app/api/endpoints/filters.py

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends, Request
from sqlalchemy.orm import Session
from pydantic import ValidationError
from app.schemas import QuestionSchema, FilterParamsSchema
from app.crud import filter_questions_crud
from app.db import get_db

router = APIRouter()

async def forbid_extra_params(request: Request):
    allowed_params = {'subject', 'topic', 'subtopic', 'difficulty', 'tags', 'skip', 'limit'}
    actual_params = set(request.query_params.keys())
    extra_params = actual_params - allowed_params
    if extra_params:
        raise HTTPException(status_code=422, detail=f"Unexpected parameters provided: {extra_params}")

@router.get("/questions/filter", response_model=List[QuestionSchema], status_code=200)
async def filter_questions_endpoint(
    request: Request,
    subject: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    subtopic: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    await forbid_extra_params(request)
    try:
        # Constructing the filters model from the query parameters directly
        filters = FilterParamsSchema(
            subject=subject,
            topic=topic,
            subtopic=subtopic,
            difficulty=difficulty,
            tags=tags
        )
        questions = filter_questions_crud(
            db=db,
            filters=filters.model_dump(),
            skip=skip,
            limit=limit
        )
        return questions if questions else []
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
