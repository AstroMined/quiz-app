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
which is handled by the get_current_user dependency.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from backend.app.crud.crud_user_responses import (create_user_response_in_db,
                                                  delete_user_response_from_db,
                                                  read_user_response_from_db,
                                                  read_user_responses_from_db,
                                                  update_user_response_in_db)
from backend.app.db.session import get_db
from backend.app.models.users import UserModel
from backend.app.schemas.user_responses import (UserResponseCreateSchema,
                                                UserResponseSchema,
                                                UserResponseUpdateSchema)
from backend.app.services.user_service import get_current_user

router = APIRouter()

@router.post(
    "/user-responses/",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED
)
def post_user_response(
    user_response: UserResponseCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a new user response.

    This endpoint allows authenticated users to create a new user response in the database.
    The user response data is validated using the UserResponseCreateSchema.

    Args:
        user_response (UserResponseCreateSchema): The user response data to be created.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        UserResponseSchema: The created user response data.

    Raises:
        HTTPException: If there's an error during the creation process.
    """
    user_response_data = user_response.model_dump()
    created_response = create_user_response_in_db(db=db, user_response_data=user_response_data)
    return UserResponseSchema.model_validate(created_response)

@router.get("/user-responses/{user_response_id}", response_model=UserResponseSchema)
def get_user_response(
    user_response_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retrieve a specific user response by ID.

    This endpoint allows authenticated users to retrieve a single user response by its ID.

    Args:
        user_response_id (int): The ID of the user response to retrieve.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        UserResponseSchema: The user response data.

    Raises:
        HTTPException: If the user response with the given ID is not found.
    """
    user_response = read_user_response_from_db(db, user_response_id)
    if not user_response:
        raise HTTPException(status_code=404, detail="User response not found")
    return UserResponseSchema.model_validate(user_response)

@router.get("/user-responses/", response_model=List[UserResponseSchema])
def get_user_responses(
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
    Retrieve a list of user responses.

    This endpoint allows authenticated users to retrieve a list of user responses from the database.
    The responses can be filtered by user_id, question_id, and time range.

    Args:
        user_id (Optional[int]): Filter responses by user ID.
        question_id (Optional[int]): Filter responses by question ID.
        start_time (Optional[datetime]): Filter responses after this time.
        end_time (Optional[datetime]): Filter responses before this time.
        skip (int): The number of responses to skip (for pagination).
        limit (int): The maximum number of responses to return (for pagination).
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        List[UserResponseSchema]: A list of user responses.
    """
    user_responses = read_user_responses_from_db(
        db,
        user_id=user_id,
        question_id=question_id,
        start_time=start_time,
        end_time=end_time,
        skip=skip,
        limit=limit
    )
    return [UserResponseSchema.model_validate(ur) for ur in user_responses]

@router.put("/user-responses/{user_response_id}", response_model=UserResponseSchema)
def put_user_response(
    user_response_id: int,
    user_response: UserResponseUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update a specific user response.

    This endpoint allows authenticated users to update an existing user response by its ID.

    Args:
        user_response_id (int): The ID of the user response to update.
        user_response (UserResponseUpdateSchema): The updated user response data.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        UserResponseSchema: The updated user response data.

    Raises:
        HTTPException: If the user response with the given ID is not found.
    """
    user_response_data = user_response.model_dump()
    updated_user_response = update_user_response_in_db(db, user_response_id, user_response_data)
    if not updated_user_response:
        raise HTTPException(status_code=404, detail="User response not found")
    return UserResponseSchema.model_validate(updated_user_response)

@router.delete("/user-responses/{user_response_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_response(
    user_response_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Delete a specific user response.

    This endpoint allows authenticated users to delete an existing user response by its ID.

    Args:
        user_response_id (int): The ID of the user response to delete.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        Response: An empty response with a 204 status code.

    Raises:
        HTTPException: If the user response with the given ID is not found.
    """
    success = delete_user_response_from_db(db, user_response_id)
    if not success:
        raise HTTPException(status_code=404, detail="User response not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
