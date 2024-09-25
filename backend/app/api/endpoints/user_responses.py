# filename: backend/app/api/endpoints/user_responses.py

"""
User Responses Management API

This module provides API endpoints for managing user responses in the quiz application.
It includes operations for creating, reading, updating, and deleting user responses.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_user_responses module.

Endpoints:
- POST /user-responses/: Create a new user response
- GET /user-responses/{user_response_id}: Retrieve a specific user response by ID
- GET /user-responses/: Retrieve a list of user responses
- PUT /user-responses/{user_response_id}: Update a specific user response
- DELETE /user-responses/{user_response_id}: Delete a specific user response

Each endpoint requires appropriate authentication and authorization,
which is handled by the check_auth_status and get_current_user_or_error functions.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from backend.app.crud.crud_answer_choices import read_answer_choice_from_db
from backend.app.crud.crud_questions import read_question_from_db
from backend.app.crud.crud_user_responses import (
    create_user_response_in_db,
    delete_user_response_from_db,
    read_user_response_from_db,
    read_user_responses_from_db,
    update_user_response_in_db,
)
from backend.app.db.session import get_db
from backend.app.schemas.user_responses import (
    UserResponseCreateSchema,
    UserResponseSchema,
    UserResponseUpdateSchema,
)
from backend.app.services.auth_utils import check_auth_status, get_current_user_or_error

router = APIRouter()


def score_user_response(db: Session, user_response_data: dict) -> bool:
    """
    Score the user response by checking if the selected answer is correct.

    Args:
        db (Session): The database session.
        user_response_data (dict): The user response data.

    Returns:
        bool: True if the answer is correct, False otherwise.

    Raises:
        HTTPException: If the question or answer choice is not found.
    """
    question = read_question_from_db(db, user_response_data["question_id"])
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    answer_choice = read_answer_choice_from_db(
        db, user_response_data["answer_choice_id"]
    )
    if not answer_choice:
        raise HTTPException(status_code=404, detail="Answer choice not found")

    return answer_choice.is_correct


@router.post(
    "/user-responses/",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
def post_user_response(
    request: Request,
    user_response: UserResponseCreateSchema,
    db: Session = Depends(get_db),
):
    """
    Create a new user response and score it.

    This endpoint allows authenticated users to create a new user response in the database.
    The user response data is validated using the UserResponseCreateSchema.
    After creation, the response is immediately scored.

    Args:
        request (Request): The FastAPI request object.
        user_response (UserResponseCreateSchema): The user response data to be created.
        db (Session): The database session.

    Returns:
        UserResponseSchema: The created and scored user response data.

    Raises:
        HTTPException: If there's an error during the creation or scoring process, or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    user_response_data = user_response.model_dump()

    try:
        is_correct = score_user_response(db, user_response_data)
        user_response_data["is_correct"] = is_correct
    except HTTPException as e:
        # If scoring fails, we still create the response but set is_correct to None
        user_response_data["is_correct"] = None

    created_response = create_user_response_in_db(
        db=db, user_response_data=user_response_data
    )
    return UserResponseSchema.model_validate(created_response)


@router.get("/user-responses/{user_response_id}", response_model=UserResponseSchema)
def get_user_response(
    request: Request, user_response_id: int, db: Session = Depends(get_db)
):
    """
    Retrieve a specific user response by ID.

    This endpoint allows authenticated users to retrieve a single user response by its ID.

    Args:
        request (Request): The FastAPI request object.
        user_response_id (int): The ID of the user response to retrieve.
        db (Session): The database session.

    Returns:
        UserResponseSchema: The user response data.

    Raises:
        HTTPException: If the user response with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    user_response = read_user_response_from_db(db, user_response_id)
    if not user_response:
        raise HTTPException(status_code=404, detail="User response not found")
    return UserResponseSchema.model_validate(user_response)


@router.get("/user-responses/", response_model=List[UserResponseSchema])
def get_user_responses(
    request: Request,
    user_id: Optional[int] = None,
    question_id: Optional[int] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of user responses.

    This endpoint allows authenticated users to retrieve a list of user responses from the database.
    The responses can be filtered by user_id, question_id, and time range.

    Args:
        request (Request): The FastAPI request object.
        user_id (Optional[int]): Filter responses by user ID.
        question_id (Optional[int]): Filter responses by question ID.
        start_time (Optional[datetime]): Filter responses after this time.
        end_time (Optional[datetime]): Filter responses before this time.
        skip (int): The number of responses to skip (for pagination).
        limit (int): The maximum number of responses to return (for pagination).
        db (Session): The database session.

    Returns:
        List[UserResponseSchema]: A list of user responses.

    Raises:
        HTTPException: If the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    user_responses = read_user_responses_from_db(
        db,
        user_id=user_id,
        question_id=question_id,
        start_time=start_time,
        end_time=end_time,
        skip=skip,
        limit=limit,
    )
    return [UserResponseSchema.model_validate(ur) for ur in user_responses]


@router.put("/user-responses/{user_response_id}", response_model=UserResponseSchema)
def put_user_response(
    request: Request,
    user_response_id: int,
    user_response: UserResponseUpdateSchema,
    db: Session = Depends(get_db),
):
    """
    Update a specific user response.

    This endpoint allows authenticated users to update an existing user response by its ID.

    Args:
        request (Request): The FastAPI request object.
        user_response_id (int): The ID of the user response to update.
        user_response (UserResponseUpdateSchema): The updated user response data.
        db (Session): The database session.

    Returns:
        UserResponseSchema: The updated user response data.

    Raises:
        HTTPException: If the user response with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    user_response_data = user_response.model_dump()
    updated_user_response = update_user_response_in_db(
        db, user_response_id, user_response_data
    )
    if not updated_user_response:
        raise HTTPException(status_code=404, detail="User response not found")
    return UserResponseSchema.model_validate(updated_user_response)


@router.delete(
    "/user-responses/{user_response_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_user_response(
    request: Request, user_response_id: int, db: Session = Depends(get_db)
):
    """
    Delete a specific user response.

    This endpoint allows authenticated users to delete an existing user response by its ID.

    Args:
        request (Request): The FastAPI request object.
        user_response_id (int): The ID of the user response to delete.
        db (Session): The database session.

    Returns:
        Response: An empty response with a 204 status code.

    Raises:
        HTTPException: If the user response with the given ID is not found or if the user is not authenticated.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    success = delete_user_response_from_db(db, user_response_id)
    if not success:
        raise HTTPException(status_code=404, detail="User response not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
