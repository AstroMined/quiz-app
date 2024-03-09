# filename: app/api/endpoints/user_responses.py
"""
This module provides endpoints for managing user responses.

It defines routes for creating and retrieving user responses.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.crud.crud_user_responses import create_user_response, get_user_responses
from app.db.session import get_db
from app.schemas.user_responses import UserResponse, UserResponseCreate

router = APIRouter()

@router.post("/user-responses/", response_model=UserResponse, status_code=201)
def create_user_response_endpoint(user_response: UserResponseCreate, db: Session = Depends(get_db)):
    """
    Create a new user response.

    Args:
        user_response (UserResponseCreate): The user response data.
        db (Session): The database session.

    Returns:
        UserResponse: The created user response.
    """
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