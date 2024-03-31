# filename: app/api/endpoints/users.py
"""
This module provides a simple endpoint for retrieving user information.

It defines a route for retrieving a list of users (currently hardcoded).
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.users import User as UserModel
from app.crud.crud_user import create_user as create_user_crud  # Import from crud_user module
from app.schemas.user import UserCreate as UserCreateSchema, User as UserSchema
from app.core.auth import get_current_user

router = APIRouter()

@router.get("/users/", response_model=List[UserSchema])
def read_users(db: Session = Depends(get_db), current_user: UserModel = Depends(get_current_user)):
    users = db.query(UserModel).all()
    return users

@router.post("/users/", response_model=UserSchema, status_code=201)
def create_user(user: UserCreateSchema, db: Session = Depends(get_db)):
    """
    Create a new user in the database.

    This endpoint receives user data as a request payload, validates it against
    the UserCreateSchema, and then proceeds to create a new user record in the
    database using the provided details. It returns the newly created user data
    as per the UserModelSchema.

    Args:
        user (UserCreateSchema): The user information required to create a new user.
                                  This includes, but is not limited to, the username
                                  and password.
        db (Session, optional): The database session used to perform database
                                operations. This dependency is injected by FastAPI
                                via Depends(get_db).

    Returns:
        UserModelSchema: The schema of the newly created user, which includes
                         the user's id, username, and other fields as defined
                         in the schema but not including sensitive information
                         like passwords.

    Raises:
        HTTPException: A 400 error if the user creation process fails, which
                       could occur if the username already exists.
    """
    # Attempt to create a new user in the database using CRUD operations
    try:
        new_user = create_user_crud(db=db, user=user)
        return new_user
    except Exception as e:
        # If there's an error (e.g., username already exists), raise an HTTPException
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Failed to create user. ' + str(e)
            ) from e
