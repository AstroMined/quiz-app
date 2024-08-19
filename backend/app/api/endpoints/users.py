# filename: backend/app/api/endpoints/users.py

"""
Users Management API

This module provides API endpoints for managing users in the quiz application.
It includes operations for creating, reading, and updating user information.

The module uses FastAPI for defining the API endpoints and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_user module.

Endpoints:
- POST /users/: Create a new user
- GET /users/: Retrieve a list of users
- GET /users/me: Retrieve the current user's information
- PUT /users/me: Update the current user's information

Each endpoint requires appropriate authentication and authorization,
which is handled by the get_current_user dependency.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.crud.crud_user import (create_user_in_db, read_users_from_db,
                                        update_user_in_db)
from backend.app.db.session import get_db
from backend.app.models.users import UserModel
from backend.app.schemas.user import (UserCreateSchema, UserSchema,
                                      UserUpdateSchema)
from backend.app.services.user_service import get_current_user

router = APIRouter()

@router.post("/users/", response_model=UserSchema, status_code=201)
def post_user(
    user: UserCreateSchema, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a new user.

    This endpoint allows authenticated users to create a new user in the database.
    The user data is validated using the UserCreateSchema.

    Args:
        user (UserCreateSchema): The user data to be created.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        UserSchema: The created user data.

    Raises:
        HTTPException: If there's an error during the creation process.
    """
    user_data = user.model_dump()
    try:
        new_user = create_user_in_db(db=db, user_data=user_data)
        return UserSchema.model_validate(new_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Failed to create user. ' + str(e)
        ) from e

@router.get("/users/", response_model=List[UserSchema])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retrieve a list of users.

    This endpoint allows authenticated users to retrieve a paginated list of users from the database.

    Args:
        skip (int, optional): The number of users to skip. Defaults to 0.
        limit (int, optional): The maximum number of users to return. Defaults to 100.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        List[UserSchema]: A list of users.
    """
    users = read_users_from_db(db, skip=skip, limit=limit)
    return [UserSchema.model_validate(user) for user in users]

@router.get("/users/me", response_model=UserSchema)
def get_user_me(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Retrieve the current user's information.

    This endpoint allows authenticated users to retrieve their own user information.

    Args:
        current_user (UserModel): The authenticated user making the request.

    Returns:
        UserSchema: The current user's data.
    """
    return UserSchema.model_validate(current_user)

@router.put("/users/me", response_model=UserSchema)
def put_user_me(
    user: UserUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update the current user's information.

    This endpoint allows authenticated users to update their own user information.

    Args:
        user (UserUpdateSchema): The updated user data.
        db (Session): The database session.
        current_user (UserModel): The authenticated user making the request.

    Returns:
        UserSchema: The updated user data.

    Raises:
        HTTPException: 
            - 400 Bad Request: If there's a validation error.
            - 500 Internal Server Error: If there's an unexpected error during the update process.
    """
    user_data = user.model_dump()
    try:
        updated_user = update_user_in_db(db=db, user_id=current_user.id, user_data=user_data)
        return UserSchema.model_validate(updated_user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except HTTPException as e:
        raise e
