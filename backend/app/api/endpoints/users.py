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

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import ValidationError

from backend.app.crud.crud_user import (create_user_in_db, read_users_from_db,
                                        update_user_in_db)
from backend.app.crud.crud_roles import read_role_from_db
from backend.app.db.session import get_db
from backend.app.schemas.user import (UserCreateSchema, UserSchema,
                                      UserUpdateSchema)
from backend.app.services.auth_utils import check_auth_status, get_current_user_or_error
from backend.app.core.security import get_password_hash

router = APIRouter()

@router.post("/users/", response_model=UserSchema, status_code=201)
def post_user(
    request: Request,
    user: UserCreateSchema, 
    db: Session = Depends(get_db)
):
    """
    Create a new user.

    This endpoint allows authenticated users to create a new user in the database.
    The user data is validated using the UserCreateSchema.

    Args:
        request (Request): The FastAPI request object.
        user (UserCreateSchema): The user data to be created.
        db (Session): The database session.

    Returns:
        UserSchema: The created user data.

    Raises:
        HTTPException: If there's an error during the creation process.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    try:
        user_data = user.model_dump()
        user_data['hashed_password'] = get_password_hash(user_data.pop('password'))
        new_user = create_user_in_db(db=db, user_data=user_data)
        return UserSchema.model_validate(new_user)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.errors()
        ) from e
    except ValueError as e:
        if "already exists" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            ) from e
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Failed to create user. ' + str(e)
        ) from e

@router.get("/users/", response_model=List[UserSchema])
def get_users(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of users.

    This endpoint allows authenticated users to retrieve a paginated list of users from the database.

    Args:
        request (Request): The FastAPI request object.
        skip (int, optional): The number of users to skip. Defaults to 0.
        limit (int, optional): The maximum number of users to return. Defaults to 100.
        db (Session): The database session.

    Returns:
        List[UserSchema]: A list of users.
    """
    check_auth_status(request)
    get_current_user_or_error(request)

    users = read_users_from_db(db, skip=skip, limit=limit)
    return [UserSchema.model_validate(user) for user in users]

@router.get("/users/me", response_model=UserSchema)
def get_user_me(request: Request):
    """
    Retrieve the current user's information.

    This endpoint allows authenticated users to retrieve their own user information.

    Args:
        request (Request): The FastAPI request object.

    Returns:
        UserSchema: The current user's data.
    """
    check_auth_status(request)
    current_user = get_current_user_or_error(request)
    return UserSchema.model_validate(current_user)

@router.put("/users/me", response_model=UserSchema)
def put_user_me(
    request: Request,
    user: UserUpdateSchema,
    db: Session = Depends(get_db)
):
    """
    Update the current user's information.

    This endpoint allows authenticated users to update their own user information.

    Args:
        request (Request): The FastAPI request object.
        user (UserUpdateSchema): The updated user data.
        db (Session): The database session.

    Returns:
        UserSchema: The updated user data.

    Raises:
        HTTPException: 
            - 422 Unprocessable Entity: If there's a validation error or invalid role_id.
            - 400 Bad Request: If there's an unexpected error during the update process.
    """
    check_auth_status(request)
    current_user = get_current_user_or_error(request)

    try:
        user_data = user.model_dump(exclude_unset=True)
        if 'password' in user_data:
            user_data['hashed_password'] = get_password_hash(user_data.pop('password'))
        if 'role_id' in user_data:
            role = read_role_from_db(db, user_data['role_id'])
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Invalid role_id"
                )
        
        updated_user = update_user_in_db(db=db, user_id=current_user.id, user_data=user_data)
        if updated_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserSchema.model_validate(updated_user)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.errors()
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        ) from e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Failed to update user. ' + str(e)
        ) from e
