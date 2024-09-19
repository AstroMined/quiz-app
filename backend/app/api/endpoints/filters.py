# filename: backend/app/api/endpoints/filters.py

"""
Filters API

This module provides API endpoints for filtering questions in the quiz application.
It includes an operation for retrieving filtered questions based on various criteria.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_filters module.

Endpoints:
- GET /questions/filter: Retrieve a list of filtered questions

The endpoint requires appropriate authentication and authorization,
which is handled by the check_auth_status and get_current_user_or_error functions.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from backend.app.crud.crud_filters import read_filtered_questions_from_db
from backend.app.db.session import get_db
from backend.app.schemas.filters import FilterParamsSchema
from backend.app.schemas.questions import QuestionSchema
from backend.app.services.auth_utils import check_auth_status, get_current_user_or_error
from backend.app.core.config import DifficultyLevel

router = APIRouter()

async def forbid_extra_params(request: Request):
    """
    Check for unexpected query parameters in the request.

    This function ensures that only allowed query parameters are present in the request.

    Args:
        request (Request): The incoming request object.

    Raises:
        HTTPException: If unexpected parameters are found in the request.
    """
    allowed_params = {'subject', 'topic', 'subtopic', 'difficulty', 'question_tags', 'skip', 'limit'}
    actual_params = set(request.query_params.keys())
    extra_params = actual_params - allowed_params
    if extra_params:
        raise HTTPException(status_code=422, detail=f"Unexpected parameters provided: {extra_params}")

@router.get("/questions/filter", response_model=List[QuestionSchema], status_code=200)
async def filter_questions(
    request: Request,
    subject: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    subtopic: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    question_tags: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieve a list of filtered questions.

    This endpoint allows authenticated users to retrieve a list of questions
    filtered by various criteria such as subject, topic, subtopic, difficulty, and tags.

    Args:
        request (Request): The incoming request object.
        subject (Optional[str]): The subject to filter by.
        topic (Optional[str]): The topic to filter by.
        subtopic (Optional[str]): The subtopic to filter by.
        difficulty (Optional[str]): The difficulty level to filter by.
        question_tags (Optional[List[str]]): A list of tags to filter by.
        db (Session): The database session.
        skip (int): The number of questions to skip (for pagination).
        limit (int): The maximum number of questions to return (for pagination).

    Returns:
        List[QuestionSchema]: A list of filtered questions.

    Raises:
        HTTPException: If unexpected parameters are provided in the request, if an invalid difficulty level is specified,
                       or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    await forbid_extra_params(request)
    
    # Convert difficulty string to DifficultyLevel enum
    difficulty_enum = None
    if difficulty:
        try:
            difficulty_enum = DifficultyLevel[difficulty.upper()]
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid difficulty level: {difficulty}")
    
    filters = FilterParamsSchema(
        subject=subject,
        topic=topic,
        subtopic=subtopic,
        difficulty=difficulty_enum,
        question_tags=question_tags
    )
    
    questions = read_filtered_questions_from_db(
        db=db,
        filters=filters.model_dump(),
        skip=skip,
        limit=limit
    )
    
    return [QuestionSchema.model_validate(q) for q in questions] if questions else []
