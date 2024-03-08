# filename: app/core/jwt.py
"""
This module provides JWT (JSON Web Token) related functionality for the Quiz App backend.

It includes functions for creating and verifying JWT access tokens, as well as managing token expiration and other JWT-related operations.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_for_testing_purposes")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a new access token.

    Args:
        data (dict): The data to be encoded in the access token.
        expires_delta (Optional[timedelta]): The optional expiration time for the token.

    Returns:
        str: The generated access token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    """
    Verify the provided JWT token.

    Args:
        token (str): The JWT token to be verified.
        credentials_exception: The exception to be raised if the token is invalid.

    Returns:
        str: The username extracted from the verified token.

    Raises:
        credentials_exception: If the token is invalid or the username is missing.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception