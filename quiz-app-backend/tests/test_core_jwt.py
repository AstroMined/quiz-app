# filename: tests/test_core_jwt.py
import pytest
from datetime import datetime, timedelta
from jose import JWTError
from app.core import jwt

def test_jwt_token_creation_and_verification():
    """
    Test the JWT token creation and verification process.
    """
    test_data = {"sub": "testuser"}
    token = jwt.create_access_token(data=test_data, expires_delta=timedelta(minutes=30))
    assert token is not None
    decoded_sub = jwt.verify_token(token, credentials_exception=ValueError("Invalid token"))
    assert decoded_sub == test_data["sub"], "Decoded subject does not match the expected value."

def test_create_access_token_with_expiration():
    """
    Test creating an access token with a specific expiration time.
    """
    expires_delta = timedelta(minutes=30)
    access_token = jwt.create_access_token(data={"sub": "testuser"}, expires_delta=expires_delta)
    assert access_token is not None

def test_verify_token_invalid():
    """
    Test verifying an invalid token.
    """
    invalid_token = "invalid_token"
    with pytest.raises(JWTError):
        jwt.verify_token(invalid_token, credentials_exception=JWTError)

def test_verify_token_expired():
    """
    Test verifying an expired token.
    """
    expires_delta = timedelta(minutes=-1)  # Expired token
    expired_token = jwt.create_access_token(data={"sub": "testuser"}, expires_delta=expires_delta)
    with pytest.raises(JWTError):
        jwt.verify_token(expired_token, credentials_exception=JWTError)
