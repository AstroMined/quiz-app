# filename: app/api/endpoints/user_responses.py
"""
User Responses API Endpoints.
This module defines the API endpoints for managing user responses in the application.

It includes endpoints to create, read, update, and delete user responses.
It also includes a service to get the current user, the database session, 
and CRUD operations to manage user responses.

Imports:
----------
typing: For type hinting.
fastapi: For creating API routes and handling HTTP exceptions.
sqlalchemy.orm: For handling database sessions.
app.crud: For performing CRUD operations on the user responses.
app.db: For getting the database session.
app.schemas: For validating and deserializing user response data.
app.models: For accessing the user, question, and answer choice models.

Variables:
----------
router: The API router instance.

Endpoints:
----------
- POST /user-responses/:
    Create a new user response.

- GET /user-responses/{user_response_id}:
    Get a user response by ID.

- GET /user-responses/:
    Get a list of user responses.

- PUT /user-responses/{user_response_id}:
    Update a user response.

- DELETE /user-responses/{user_response_id}:
    Delete a user response.
"""

from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from app.crud import (
    create_user_response_crud,
    get_user_response_crud,
    get_user_responses_crud,
    update_user_response_crud,
    delete_user_response_crud
)
from app.db import get_db
from app.schemas import UserResponseSchema, UserResponseCreateSchema, UserResponseUpdateSchema
from app.models import AnswerChoiceModel, UserModel, QuestionModel
from app.services import get_current_user

router = APIRouter()


@router.post(
    "/user-responses/",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED
)
# pylint: disable=unused-argument
def create_user_response_endpoint(
    user_response: UserResponseCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a new user response.

    Args:
        user_response (UserResponseCreateSchema):
            The user response data.
        db (Session, optional):
            The database session. Defaults to Depends(get_db).
        current_user (UserModel, optional):
            The current authenticated user. Defaults to Depends(get_current_user).

    Returns:
        UserResponseSchema: The created user response.

    Raises:
        HTTPException: If the user_id, question_id, or answer_choice_id is invalid.
    """
    user = db.query(UserModel).filter(
        UserModel.id == user_response.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_id")

    question = db.query(QuestionModel).filter(
        QuestionModel.id == user_response.question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid question_id")

    answer_choice = db.query(AnswerChoiceModel).filter(
        AnswerChoiceModel.id == user_response.answer_choice_id).first()
    if not answer_choice:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid answer_choice_id"
        )

    user_response.timestamp = datetime.now(timezone.utc)
    return create_user_response_crud(db=db, user_response=user_response)


@router.get("/user-responses/{user_response_id}", response_model=UserResponseSchema)
# pylint: disable=unused-argument
def get_user_response_endpoint(
    user_response_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get a user response by ID.

    Args:
        user_response_id (int):
            The ID of the user response.
        db (Session, optional):
            The database session. Defaults to Depends(get_db).
        current_user (UserModel, optional):
            The current authenticated user. Defaults to Depends(get_current_user).

    Returns:
        UserResponseSchema: The user response with the specified ID.

    Raises:
        HTTPException: If the user response is not found.

    Example:
        >>> get_user_response_endpoint(1)
        {
            "id": 1,
            "question_id": 1,
            "user_id": 1,
            "response": "Option A",
            "created_at": "2022-01-01 12:00:00",
            "updated_at": "2022-01-01 12:05:00"
        }
    """
    user_response = get_user_response_crud(db, user_response_id)
    if not user_response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User response not found")
    return user_response


@router.get("/user-responses/", response_model=List[UserResponseSchema])
# pylint: disable=unused-argument
def get_user_responses_endpoint(
    user_id: Optional[int] = None,
    question_id: Optional[int] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get a list of user responses.

    Args:
        user_id (int, optional): The ID of the user. Defaults to None.
        question_id (int, optional): The ID of the question. Defaults to None.
        start_time (datetime, optional): The start time of the responses. Defaults to None.
        end_time (datetime, optional): The end time of the responses. Defaults to None.
        skip (int, optional): The number of user responses to skip. Defaults to 0.
        limit (int, optional): The maximum number of user responses to retrieve. Defaults to 100.
        db (Session, optional): The database session. Defaults to Depends(get_db).
        current_user (UserModel, optional): The current user. Defaults to Depends(get_current_user).

    Returns:
        List[UserResponseSchema]: The list of user responses.

    """
    user_responses = get_user_responses_crud(
        db,
        user_id=user_id,
        question_id=question_id,
        start_time=start_time,
        end_time=end_time,
        skip=skip,
        limit=limit
    )
    return user_responses


@router.put("/user-responses/{user_response_id}", response_model=UserResponseSchema)
# pylint: disable=unused-argument
def update_user_response_endpoint(
    user_response_id: int,
    user_response: UserResponseUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update a user response.

    Args:
        user_response_id (int):
            The ID of the user response to update.
        user_response (UserResponseUpdateSchema):
            The updated user response data.
        db (Session, optional):
            The database session. Defaults to Depends(get_db).
        current_user (UserModel, optional):
            The current authenticated user. Defaults to Depends(get_current_user).

    Returns:
        UserResponseSchema: The updated user response.

    """
    updated_user_response = update_user_response_crud(
        db, user_response_id, user_response)
    return updated_user_response


@router.delete("/user-responses/{user_response_id}", status_code=status.HTTP_204_NO_CONTENT)
# pylint: disable=unused-argument
def delete_user_response_endpoint(
    user_response_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete a user response.

    Args:
        user_response_id (int):
            The ID of the user response to delete.
        db (Session, optional):
            The database session. Defaults to Depends(get_db).
        current_user (UserModel, optional):
            The current authenticated user. Defaults to Depends(get_current_user).

    Returns:
        Response: The HTTP response with status code 204 (No Content).

    """
    delete_user_response_crud(db, user_response_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
