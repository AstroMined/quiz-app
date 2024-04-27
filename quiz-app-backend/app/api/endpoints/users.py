# filename: app/api/endpoints/users.py
"""
This module defines the API endpoints for managing users in the application.

It includes endpoints to create and read users.
It also includes services to get the database session and the current user, 
and CRUD operations to manage users.

Imports:
----------
typing: For type hinting.
fastapi: For creating API routes and handling HTTP exceptions.
sqlalchemy.orm: For handling database sessions.
app.db.session: For getting the database session.
app.models.users: For accessing the user model.
app.crud: For performing CRUD operations on the users.
app.schemas.user: For validating and deserializing user data.
app.services: For getting the current user.

Variables:
----------
router: The API router instance.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.users import UserModel
from app.crud import create_user_crud, update_user_crud
from app.schemas.user import UserCreateSchema, UserSchema, UserUpdateSchema
from app.services import get_current_user

router = APIRouter()

@router.get("/users/", response_model=List[UserSchema])
# pylint: disable=unused-argument
def read_users(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    """
    Retrieve a list of all users.

    Parameters:
        db (Session): The database session.
        current_user (UserModel): The current user.

    Returns:
        List[UserSchema]: A list of user objects.
    """
    users = db.query(UserModel).all()
    return users

@router.post("/users/", response_model=UserSchema, status_code=201)
def create_user(user: UserCreateSchema, db: Session = Depends(get_db)):
    """
    Create a new user.

    Parameters:
        user (UserCreateSchema): The user data to be created.
        db (Session): The database session.

    Returns:
        UserSchema: The created user object.

    Raises:
        HTTPException: If there's an error creating the user.
    """
    try:
        new_user = create_user_crud(db=db, user=user)
        return new_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Failed to create user. ' + str(e)
            ) from e

@router.get("/users/me", response_model=UserSchema)
def read_user_me(current_user: UserModel = Depends(get_current_user)):
    """
    Retrieve the current user.

    Parameters:
        current_user (UserModel): The current user.

    Returns:
        UserSchema: The current user object.
    """
    return current_user

@router.put("/users/me", response_model=UserSchema)
def update_user_me(
    updated_user: UserUpdateSchema,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the current user.

    Parameters:
        updated_user (UserUpdateSchema): The updated user data.
        current_user (UserModel): The current user.
        db (Session): The database session.

    Returns:
        UserSchema: The updated user object.
    """
    return update_user_crud(db=db, user_id=current_user.id, updated_user=updated_user)
