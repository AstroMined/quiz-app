# filename: app/crud/crud_user_responses.py
"""
This module provides CRUD operations for user responses.

It includes functions for creating and retrieving user responses.
"""

from typing import List
from sqlalchemy.orm import Session
from app.models import UserResponse
from app.schemas import UserResponseCreate

def create_user_response(db: Session, user_response: UserResponseCreate) -> UserResponse:
    """
    Create a new user response.

    Args:
        db (Session): The database session.
        user_response (UserResponseCreate): The user response data.

    Returns:
        UserResponse: The created user response.
    """
    db_user_response = UserResponse(**user_response.dict())
    db.add(db_user_response)
    db.commit()
    db.refresh(db_user_response)
    return db_user_response

def get_user_responses(db: Session, skip: int = 0, limit: int = 100) -> List[UserResponse]:
    """
    Retrieve a list of user responses.

    Args:
        db (Session): The database session.
        skip (int): The number of user responses to skip.
        limit (int): The maximum number of user responses to retrieve.

    Returns:
        List[UserResponse]: The list of user responses.
    """
    return db.query(UserResponse).offset(skip).limit(limit).all()