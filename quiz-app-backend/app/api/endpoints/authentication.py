# filename: app/api/endpoints/authentication.py
"""
This module provides endpoints for user registration and authentication.

It defines routes for user registration and issuing access tokens upon successful authentication.
"""

# Import necessary libraries and modules
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import crud, models, schemas
from app.core import security, jwt
from app.db.session import SessionLocal

# Create a FastAPI router for handling authentication-related routes
router = APIRouter()

def get_db():
    """
    Dependency that creates a new database session.
    
    Yields:
        A SQLAlchemy SessionLocal instance that can be used to execute database operations.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register/")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
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
    # Check if the username is already taken
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    # Hash the user's password for security
    user.password = security.get_password_hash(user.password)
    # Create the user in the database
    return crud.create_user(db=db, user=user)

@router.post("/token/")
def login_for_access_token(form_data: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Endpoint to authenticate a user and issue a JWT access token.
    
    Args:
        form_data: A UserLogin schema object containing the user's login credentials.
        db: A database session dependency injected by FastAPI.
        
    Raises:
        HTTPException: If the username or password is incorrect.
        
    Returns:
        A dictionary containing the access token and the token type.
    """
    # Authenticate the user
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    # Set the expiration time for the access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Create the access token
    access_token = jwt.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    # Return the access token and the token type
    return {"access_token": access_token, "token_type": "bearer"}