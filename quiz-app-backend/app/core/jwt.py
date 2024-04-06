# filename: app/core/jwt.py
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from fastapi import HTTPException, status
from app.core import settings_core

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings_core.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings_core.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, settings_core.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except jwt.JWTError:
        raise credentials_exception

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings_core.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")  # Use the correct error message here
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")  # Use the correct error message here
