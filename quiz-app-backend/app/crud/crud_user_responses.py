# filename: app/crud/crud_user_responses.py
"""
This module defines the CRUD operations for user responses in the application.

It includes functions to create a new user response, retrieve a user response by its ID,
retrieve a list of user responses based on filters, update a user response, 
and delete a user response.

Imports:
----------
typing: For type hinting.
datetime: For handling date and time related tasks.
sqlalchemy.orm: For handling database sessions.
fastapi: For handling HTTP exceptions.
app.models: For accessing the user response model.
app.schemas: For validating and deserializing user response data.

Functions:
----------
create_user_response_crud: Create a new user response in the database.
get_user_response_crud: Retrieve a user response from the database by its ID.
get_user_responses_crud: Retrieve a list of user responses from the database based on filters.
update_user_response_crud: Update a user response in the database.
delete_user_response_crud: Delete a user response from the database.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import UserResponseModel
from app.schemas import UserResponseCreateSchema, UserResponseUpdateSchema


def create_user_response_crud(
    db: Session,
    user_response: UserResponseCreateSchema
) -> UserResponseModel:
    """
    Create a new user response in the database.

    Args:
        db (Session): The database session.
        user_response (UserResponseCreateSchema): The user response data.

    Returns:
        UserResponseModel: The created user response.
    """
    db_user_response = UserResponseModel(**user_response.model_dump())
    db.add(db_user_response)
    db.commit()
    db.refresh(db_user_response)
    return db_user_response


def get_user_response_crud(db: Session, user_response_id: int) -> Optional[UserResponseModel]:
    """
    Retrieve a user response from the database by its ID.

    Args:
        db (Session): The database session.
        user_response_id (int): The ID of the user response.

    Returns:
        Optional[UserResponseModel]: The retrieved user response, or None if not found.
    """
    return db.query(UserResponseModel).filter(UserResponseModel.id == user_response_id).first()


def get_user_responses_crud(
    db: Session,
    user_id: Optional[int] = None,
    question_id: Optional[int] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100
) -> List[UserResponseModel]:
    """
    Retrieve a list of user responses from the database based on the provided filters.

    Args:
        db (Session): The database session.
        user_id (Optional[int]): The ID of the user.
        question_id (Optional[int]): The ID of the question.
        start_time (Optional[datetime]): The start time of the user response.
        end_time (Optional[datetime]): The end time of the user response.
        skip (int): The number of user responses to skip.
        limit (int): The maximum number of user responses to retrieve.

    Returns:
        List[UserResponseModel]: The list of retrieved user responses.
    """
    query = db.query(UserResponseModel)

    if user_id:
        query = query.filter(UserResponseModel.user_id == user_id)
    if question_id:
        query = query.filter(UserResponseModel.question_id == question_id)
    if start_time:
        query = query.filter(UserResponseModel.timestamp >= start_time)
    if end_time:
        query = query.filter(UserResponseModel.timestamp <= end_time)

    user_responses = query.offset(skip).limit(limit).all()
    return user_responses


def update_user_response_crud(
    db: Session,
    user_response_id: int,
    user_response: UserResponseUpdateSchema
) -> UserResponseModel:
    """
    Update a user response in the database.

    Args:
        db (Session): The database session.
        user_response_id (int): The ID of the user response to update.
        user_response (UserResponseUpdateSchema): The updated user response data.

    Returns:
        UserResponseModel: The updated user response.
    """
    db_user_response = db.query(UserResponseModel).filter(
        UserResponseModel.id == user_response_id).first()
    if not db_user_response:
        raise HTTPException(status_code=404, detail="User response not found")
    update_data = user_response.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user_response, key, value)
    db.commit()
    db.refresh(db_user_response)
    return db_user_response


def delete_user_response_crud(db: Session, user_response_id: int) -> None:
    """
    Delete a user response from the database.

    Args:
        db (Session): The database session.
        user_response_id (int): The ID of the user response to delete.

    Raises:
        HTTPException: If the user response is not found.
    """
    db_user_response = db.query(UserResponseModel).filter(
        UserResponseModel.id == user_response_id).first()
    if not db_user_response:
        raise HTTPException(status_code=404, detail="User response not found")
    db.delete(db_user_response)
    db.commit()
