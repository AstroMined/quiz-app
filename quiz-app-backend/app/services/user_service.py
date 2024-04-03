# filename: app/services/user_service.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from app.core import decode_access_token
from app.crud import get_user_by_username
from app.db import get_db
from app.models import RevokedToken

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Dependency to get the current authenticated user.

    Args:
        token (str): The JWT access token.
        db (Session): The database session.

    Returns:
        User: The authenticated user.

    Raises:
        HTTPException: If the token is invalid, expired, or revoked, or if the user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        revoked_token = db.query(RevokedToken).filter(RevokedToken.token == token).first()
        if revoked_token:
            raise credentials_exception
        user = get_user_by_username(db, username=username)
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception
