# filename: app/api/endpoints/token.py
"""
This module provides an endpoint for user authentication and token generation.
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.services.auth_service import authenticate_user
from app.core import create_access_token, settings_core
from app.db import get_db
from app.schemas import TokenSchema

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.post("/token", response_model=TokenSchema)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Endpoint to authenticate a user and issue a JWT access token.
    
    Args:
        form_data: An OAuth2PasswordRequestForm object containing the user's login credentials.
        db: A database session dependency injected by FastAPI.
        
    Raises:
        HTTPException: If the username or password is incorrect, or if an internal server error occurs.
        
    Returns:
        Token: A Token object containing the access token and token type.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=settings_core.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
