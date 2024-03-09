# filename: app/api/endpoints/register.py
"""
This module provides an endpoint for user registration.

It defines a route for registering new users by validating the provided data and creating a new user in the database.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.crud.crud_user import create_user, get_user_by_username
from app.db.session import get_db
from app.schemas.user import UserCreate

router = APIRouter()

@router.post("/register/", status_code=201)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint to register a new user.
    
    Args:
        user: A UserCreate schema object containing the user's registration information.
        db: A database session dependency injected by FastAPI.
        
    Raises:
        HTTPException: If the username is already registered.
        
    Returns:
        The newly created user object.
    """
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    user_create = UserCreate(username=user.username, password=hashed_password)
    created_user = create_user(db=db, user=user_create)
    return created_user
