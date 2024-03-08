# filename: app/api/endpoints/token.py
"""
This module provides an endpoint for user authentication and token generation.

It defines a route for authenticating users and issuing access tokens upon successful authentication.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.crud.crud_user import authenticate_user
from app.core.jwt import create_access_token
from app.db.session import get_db

router = APIRouter()

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Endpoint to authenticate a user and issue a JWT access token.
    
    Args:
        form_data: An OAuth2PasswordRequestForm object containing the user's login credentials.
        db: A database session dependency injected by FastAPI.
        
    Raises:
        HTTPException: If the username or password is incorrect, or if an internal server error occurs.
        
    Returns:
        A dictionary containing the access token and the token type.
    """
    try:
        user = authenticate_user(db, username=form_data.username, password=form_data.password)
        if not user:
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        access_token = create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Internal server error")