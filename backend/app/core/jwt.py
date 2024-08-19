# filename: backend/app/core/jwt.py

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt

from backend.app.core.config import settings_core
from backend.app.services.logging_service import logger


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings_core.ACCESS_TOKEN_EXPIRE_MINUTES)
    logger.debug("Creating access token with expiration: %s", expire)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings_core.SECRET_KEY, algorithm="HS256")
    logger.debug("Access token created: %s", encoded_jwt)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        logger.debug("Decoding access token: %s", token)
        payload = jwt.decode(token, settings_core.SECRET_KEY, algorithms=["HS256"])
        logger.debug("Access token decoded: %s", payload)
        return payload
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except JWTError:
        logger.error("Invalid token")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, settings_core.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except jwt.JWTError:
        raise credentials_exception
