# filename: app/api/endpoints/user_responses.py
"""
This module defines the API endpoints for managing user responses in the application.

It includes endpoints to create, read, update, and delete user responses.
It also includes a service to get the database session and CRUD operations to manage user responses.

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
"""

from typing import List
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
        user_response (UserResponseCreateSchema): The user response data.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        UserResponseSchema: The created user response.
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
        user_response_id (int): The ID of the user response.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        UserResponseSchema: The user response with the specified ID.

    Raises:
        HTTPException: If the user response is not found.
    """
    user_response = get_user_response_crud(db, user_response_id)
    if not user_response:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User response not found")
    return user_response


@router.get("/user-responses/", response_model=List[UserResponseSchema])
# pylint: disable=unused-argument
def get_user_responses_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get a list of user responses.

    Args:
        skip (int, optional): The number of user responses to skip. Defaults to 0.
        limit (int, optional): The maximum number of user responses to retrieve. Defaults to 100.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        List[UserResponseSchema]: The list of user responses.

    """
    user_responses = get_user_responses_crud(db, skip=skip, limit=limit)
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
        user_response_id (int): The ID of the user response to update.
        user_response (UserResponseUpdateSchema): The updated user response data.
        db (Session, optional): The database session. Defaults to Depends(get_db).

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
        user_response_id (int): The ID of the user response to delete.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        Response: The HTTP response with status code 204 (No Content).

    """
    delete_user_response_crud(db, user_response_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
