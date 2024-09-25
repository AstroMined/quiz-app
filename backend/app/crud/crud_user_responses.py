# filename: backend/app/crud/crud_user_responses.py

"""
This module handles CRUD operations for user responses in the database.

It provides functions for creating, reading, updating, and deleting user responses,
as well as retrieving user responses based on various criteria such as user ID,
question ID, and time range.

Key dependencies:
- sqlalchemy.orm: For database session management
- backend.app.models.user_responses: For the UserResponseModel

Main functions:
- create_user_response_in_db: Creates a new user response
- read_user_response_from_db: Retrieves a single user response by ID
- read_user_responses_from_db: Retrieves multiple user responses with filters and pagination
- update_user_response_in_db: Updates an existing user response
- delete_user_response_from_db: Deletes a user response
- read_user_responses_for_user_from_db: Retrieves all responses for a specific user
- read_user_responses_for_question_from_db: Retrieves all responses for a specific question

Usage example:
    from sqlalchemy.orm import Session
    from backend.app.crud.crud_user_responses import create_user_response_in_db

    def add_new_user_response(db: Session, user_id: int, question_id: int,
                              answer_choice_id: int, is_correct: bool):
        user_response_data = {
            "user_id": user_id,
            "question_id": question_id,
            "answer_choice_id": answer_choice_id,
            "is_correct": is_correct
        }
        return create_user_response_in_db(db, user_response_data)
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from backend.app.models.user_responses import UserResponseModel


def create_user_response_in_db(
    db: Session, user_response_data: Dict
) -> UserResponseModel:
    """
    Create a new user response in the database.

    Args:
        db (Session): The database session.
        user_response_data (Dict): A dictionary containing the user response data.
            Required keys: "user_id", "question_id", "answer_choice_id", "is_correct"
            Optional keys: "response_time", "timestamp"

    Returns:
        UserResponseModel: The created user response database object.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        user_response_data = {
            "user_id": 1,
            "question_id": 2,
            "answer_choice_id": 3,
            "is_correct": True,
            "response_time": 10.5
        }
        new_response = create_user_response_in_db(db, user_response_data)
    """
    db_user_response = UserResponseModel(
        user_id=user_response_data["user_id"],
        question_id=user_response_data["question_id"],
        answer_choice_id=user_response_data["answer_choice_id"],
        is_correct=user_response_data["is_correct"],
        response_time=user_response_data.get("response_time"),
        timestamp=user_response_data.get("timestamp", datetime.now(timezone.utc)),
    )
    db.add(db_user_response)
    db.commit()
    db.refresh(db_user_response)
    return db_user_response


def read_user_response_from_db(
    db: Session, user_response_id: int
) -> Optional[UserResponseModel]:
    """
    Retrieve a single user response from the database by its ID.

    Args:
        db (Session): The database session.
        user_response_id (int): The ID of the user response to retrieve.

    Returns:
        Optional[UserResponseModel]: The retrieved user response database object,
        or None if not found.

    Usage example:
        response = read_user_response_from_db(db, 1)
        if response:
            print(f"User response: {response.is_correct}")
    """
    return (
        db.query(UserResponseModel)
        .filter(UserResponseModel.id == user_response_id)
        .first()
    )


def read_user_responses_from_db(
    db: Session,
    filters: Dict[str, any],
    skip: int = 0,
    limit: int = 100,
) -> List[UserResponseModel]:
    """
    Retrieve a list of user responses from the database with filters and pagination.

    Args:
        db (Session): The database session.
        filters (Dict[str, any]): A dictionary of filters to apply.
            Possible keys: "user_id", "question_id", "start_time", "end_time"
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The maximum number of records to return. Defaults to 100.

    Returns:
        List[UserResponseModel]: A list of retrieved user response database objects.

    Usage example:
        filters = {
            "user_id": 1,
            "start_time": datetime(2023, 1, 1)
        }
        responses = read_user_responses_from_db(db, filters=filters, limit=50)
        for response in responses:
            print(f"Response: {response.is_correct}, Time: {response.timestamp}")
    """
    query = db.query(UserResponseModel)

    if "user_id" in filters:
        query = query.filter(UserResponseModel.user_id == filters["user_id"])
    if "question_id" in filters:
        query = query.filter(UserResponseModel.question_id == filters["question_id"])
    if "start_time" in filters:
        query = query.filter(UserResponseModel.timestamp >= filters["start_time"])
    if "end_time" in filters:
        query = query.filter(UserResponseModel.timestamp <= filters["end_time"])

    return query.offset(skip).limit(limit).all()


def update_user_response_in_db(
    db: Session, user_response_id: int, user_response_data: Dict
) -> Optional[UserResponseModel]:
    """
    Update an existing user response in the database.

    Args:
        db (Session): The database session.
        user_response_id (int): The ID of the user response to update.
        user_response_data (Dict): A dictionary containing the updated user response data.
            Optional keys: "user_id", "question_id", "answer_choice_id", "is_correct",
                           "response_time", "timestamp"

    Returns:
        Optional[UserResponseModel]: The updated user response database object,
        or None if not found.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        updated_data = {"is_correct": False, "response_time": 15.0}
        updated_response = update_user_response_in_db(db, 1, updated_data)
        if updated_response:
            print(f"Updated response: {updated_response.is_correct}")
    """
    db_user_response = read_user_response_from_db(db, user_response_id)
    if db_user_response:
        for key, value in user_response_data.items():
            if (
                key != "is_correct" or value is not None
            ):  # Only update is_correct if it's explicitly set
                setattr(db_user_response, key, value)
        db.commit()
        db.refresh(db_user_response)
    return db_user_response


def delete_user_response_from_db(db: Session, user_response_id: int) -> bool:
    """
    Delete a user response from the database.

    Args:
        db (Session): The database session.
        user_response_id (int): The ID of the user response to delete.

    Returns:
        bool: True if the user response was successfully deleted, False otherwise.

    Raises:
        SQLAlchemyError: If there's an issue with the database operation.

    Usage example:
        if delete_user_response_from_db(db, 1):
            print("User response successfully deleted")
        else:
            print("User response not found or couldn't be deleted")
    """
    db_user_response = read_user_response_from_db(db, user_response_id)
    if db_user_response:
        db.delete(db_user_response)
        db.commit()
        return True
    return False


def read_user_responses_for_user_from_db(
    db: Session, user_id: int
) -> List[UserResponseModel]:
    """
    Retrieve all user responses for a specific user from the database.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.

    Returns:
        List[UserResponseModel]: A list of user response database objects for the specified user.

    Usage example:
        user_responses = read_user_responses_for_user_from_db(db, 1)
        for response in user_responses:
            print(f"Question ID: {response.question_id}, Is Correct: {response.is_correct}")
    """
    return (
        db.query(UserResponseModel)
        .filter(UserResponseModel.user_id == user_id)
        .all()
    )


def read_user_responses_for_question_from_db(
    db: Session, question_id: int
) -> List[UserResponseModel]:
    """
    Retrieve all user responses for a specific question from the database.

    Args:
        db (Session): The database session.
        question_id (int): The ID of the question.

    Returns:
        List[UserResponseModel]: A list of user response db objects for the specified question.

    Usage example:
        question_responses = read_user_responses_for_question_from_db(db, 1)
        for response in question_responses:
            print(f"User ID: {response.user_id}, Is Correct: {response.is_correct}")
    """
    return (
        db.query(UserResponseModel)
        .filter(UserResponseModel.question_id == question_id)
        .all()
    )
