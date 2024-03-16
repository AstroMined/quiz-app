# filename: app/api/endpoints/user_responses.py
"""
This module provides endpoints for managing user responses.

It defines routes for creating and retrieving user responses.
"""

from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.crud.crud_user_responses import create_user_response, get_user_responses
from app.db.session import get_db
from app.schemas.user_responses import UserResponse, UserResponseCreate
from app.models.users import User
from app.models.questions import Question
from app.models.answer_choices import AnswerChoice

router = APIRouter()

@router.post("/user-responses/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_response_endpoint(user_response: UserResponseCreate, db: Session = Depends(get_db)):
    """
    Create a new user response.

    Args:
        user_response (UserResponseCreate): The user response data.
        db (Session): The database session.

    Returns:
        UserResponse: The created user response.

    Raises:
        HTTPException: If the provided data is invalid or any referenced entities do not exist.
    """
    # Validate the user_id
    user = db.query(User).filter(User.id == user_response.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_id")

    # Validate the question_id
    question = db.query(Question).filter(Question.id == user_response.question_id).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid question_id")

    # Validate the answer_choice_id
    answer_choice = db.query(AnswerChoice).filter(AnswerChoice.id == user_response.answer_choice_id).first()
    if not answer_choice:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid answer_choice_id")

    return create_user_response(db=db, user_response=user_response)

@router.get("/user-responses/", response_model=List[UserResponse])
def get_user_responses_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of user responses.

    Args:
        skip (int): The number of user responses to skip.
        limit (int): The maximum number of user responses to retrieve.
        db (Session): The database session.

    Returns:
        List[UserResponse]: The list of user responses.
    """
    user_responses = get_user_responses(db, skip=skip, limit=limit)
    return user_responses
