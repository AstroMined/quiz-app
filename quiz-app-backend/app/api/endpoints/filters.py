# filename: app/api/endpoints/filters.py
"""
This module defines the API endpoints for filtering questions in the application.

It includes a function to forbid extra parameters in the request, and an endpoint 
to filter questions based on various parameters like subject, topic, subtopic, 
difficulty, tags, skip and limit.

Functions:
----------
forbid_extra_params(request: Request) -> None:
    Checks if the request contains any extra parameters that are not allowed.
    If found, raises an HTTPException.

filter_questions_endpoint(
    request: Request,
    subject: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    subtopic: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db),
    skip: int = 0, limit: int = 100
) -> List[QuestionSchema]:
    Filters questions based on the provided parameters.
    Returns a list of questions that match the filters.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.crud.crud_filters import read_filtered_questions_from_db
from app.db.session import get_db
from app.models.users import UserModel
from app.schemas.filters import FilterParamsSchema
from app.schemas.questions import QuestionSchema
from app.services.user_service import get_current_user

router = APIRouter()


async def forbid_extra_params(request: Request):
    """
    This function checks if the request contains any extra parameters that are not allowed.
    If found, it raises an HTTPException.

    Parameters:
    ----------
    request: Request
        The request object containing all the parameters.

    Raises:
    ----------
    HTTPException
        If any extra parameters are found in the request.
    """
    allowed_params = {'subject', 'topic', 'subtopic',
                      'difficulty', 'question_tags', 'skip', 'limit'}
    actual_params = set(request.query_params.keys())
    extra_params = actual_params - allowed_params
    if extra_params:
        raise HTTPException(
            status_code=422, detail=f"Unexpected parameters provided: {extra_params}")


@router.get("/questions/filter", response_model=List[QuestionSchema], status_code=200)
# pylint: disable=unused-argument
async def filter_questions_endpoint(
    request: Request,
    subject: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    subtopic: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    question_tags: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_user)
):
    """
    This function filters questions based on the provided parameters.
    Returns a list of questions that match the filters.

    Parameters:
    ----------
    request: Request
        The request object containing all the parameters.
    subject: Optional[str]
        The subject to filter the questions by.
    topic: Optional[str]
        The topic to filter the questions by.
    subtopic: Optional[str]
        The subtopic to filter the questions by.
    difficulty: Optional[str]
        The difficulty level to filter the questions by.
    question_tags: Optional[List[str]]
        The tags to filter the questions by.
    db: Session
        The database session.
    skip: int
        The number of records to skip.
    limit: int
        The maximum number of records to return.

    Returns:
    ----------
    List[QuestionSchema]
        A list of questions that match the filters.
    """
    await forbid_extra_params(request)
    try:
        # Constructing the filters model from the query parameters directly
        filters = FilterParamsSchema(
            subject=subject,
            topic=topic,
            subtopic=subtopic,
            difficulty=difficulty,
            question_tags=question_tags
        )
        questions = read_filtered_questions_from_db(
            db=db,
            filters=filters.model_dump(),
            skip=skip,
            limit=limit
        )
        return questions if questions else []
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
