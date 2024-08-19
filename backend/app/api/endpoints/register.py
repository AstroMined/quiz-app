# filename: backend/app/api/endpoints/register.py

"""
User Registration API

This module provides an API endpoint for user registration in the quiz application.
It includes an operation for creating a new user account.

The module uses FastAPI for defining the API endpoint and Pydantic for data validation.
It interacts with the database through CRUD operations defined in the crud_user module.

Endpoints:
- POST /register: Register a new user

This endpoint does not require authentication as it's used for creating new user accounts.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.security import get_password_hash
from backend.app.crud.crud_user import (create_user_in_db,
                                        read_user_by_email_from_db,
                                        read_user_by_username_from_db)
from backend.app.db.session import get_db
from backend.app.models.roles import RoleModel
from backend.app.schemas.user import UserCreateSchema, UserSchema

router = APIRouter()

@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreateSchema, db: Session = Depends(get_db)):
    """
    Register a new user.

    This endpoint allows new users to create an account in the application.
    It checks if the username and email are unique, hashes the password,
    and assigns a default role if one is not specified.

    Args:
        user (UserCreateSchema): The user data for registration.
        db (Session): The database session.

    Returns:
        UserSchema: The created user data.

    Raises:
        HTTPException: 
            - 400 Bad Request: If the username or email is already registered.
    """
    db_user = read_user_by_username_from_db(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    
    db_email = read_user_by_email_from_db(db, email=user.email)
    if db_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password.get_secret_value())
    
    if not user.role_id:
        default_role = db.query(RoleModel).filter(RoleModel.default == True).first()
        user.role_id = default_role.id if default_role else None
    
    user_data = user.model_dump()
    user_data['hashed_password'] = hashed_password
    del user_data['password']
    
    created_user = create_user_in_db(db=db, user_data=user_data)
    return UserSchema.model_validate(created_user)
