# filename: app/api/endpoints/auth.py
"""
This module defines the API endpoints for user authentication in the application.

It includes the OAuth2PasswordBearer for token authentication, 
a login endpoint to authenticate users and generate access tokens, 
and a set to store blacklisted tokens.

Imports:
----------
logging: For logging any exceptions or important actions.
fastapi: For creating API routes and handling HTTP exceptions.
sqlalchemy.orm: For handling database sessions.
jose: For handling JWT errors.
app.core: For creating access tokens and verifying passwords.
app.db: For getting the database session.
app.models: For accessing the user and revoked token models.
app.schemas: For validating and deserializing data.

Variables:
----------
logger: The logger instance.
router: The API router instance.
blacklist: A set to store blacklisted tokens.
oauth2_scheme: The OAuth2PasswordBearer instance for token authentication.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core import create_access_token, verify_password
from app.db import get_db
from app.models import UserModel, RevokedTokenModel
from app.schemas import TokenSchema, LoginFormSchema

logger = logging.getLogger(__name__)

router = APIRouter()

blacklist = set()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

@router.post("/login", response_model=TokenSchema)
async def login_endpoint(form_data: LoginFormSchema, db: Session = Depends(get_db)):
    """
    This function authenticates a user and generates an access token.

    Parameters:
    ----------
    form_data: LoginFormSchema
        The login form data containing the username and password.
    db: Session
        The database session.

    Raises:
    ----------
    HTTPException
        If the user account is inactive or the password is incorrect.

    Returns:
    ----------
    TokenSchema
        The access token for the authenticated user.
    """
    user = db.query(UserModel).filter(UserModel.username == form_data.username).first()

    if user:
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password",
                headers={"WWW-Authenticate": "Bearer"},
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_endpoint(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    This function logs out a user by adding their token to the revoked tokens list.

    Parameters:
    ----------
    token: str
        The token of the user who is logging out.
    db: Session
        The database session.

    Raises:
    ----------
    HTTPException
        If there is an error while revoking the token.

    Returns:
    ----------
    dict
        A message indicating that the user has been successfully logged out.
    """
    try:
        revoked_token = RevokedTokenModel(token=token)
        db.add(revoked_token)
        db.commit()
        return {"message": "Successfully logged out"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout user"
        ) from e
