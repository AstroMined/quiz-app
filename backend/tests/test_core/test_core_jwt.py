# filename: backend/tests/test_core/test_core_jwt.py

from datetime import timedelta, datetime, timezone
import pytest
from fastapi import HTTPException
from jose import jwt, JWTError
from unittest.mock import patch

from backend.app.core.jwt import create_access_token, decode_access_token
from backend.app.core.config import settings_core
from backend.app.models.users import UserModel

def test_create_access_token(db_session, test_model_user):
    data = {"sub": test_model_user.username}
    token = create_access_token(data)
    assert token is not None

    payload = jwt.decode(token, settings_core.SECRET_KEY, algorithms=["HS256"])
    assert payload["sub"] == test_model_user.username
    assert "exp" in payload
    assert "jti" in payload
    assert "iat" in payload

def test_create_access_token_with_expiration(db_session, test_model_user):
    data = {"sub": test_model_user.username}
    expires_delta = timedelta(minutes=30)
    token = create_access_token(data, expires_delta)
    assert token is not None

    payload = jwt.decode(token, settings_core.SECRET_KEY, algorithms=["HS256"])
    assert payload["sub"] == test_model_user.username
    expected_exp = datetime.now(timezone.utc) + expires_delta
    assert abs(payload["exp"] - expected_exp.timestamp()) < 1  # Allow 1 second difference

def test_create_access_token_user_not_found(db_session):
    data = {"sub": "nonexistent_user"}
    with pytest.raises(ValueError, match="User not found"):
        create_access_token(data)

def test_decode_access_token_valid(db_session, test_model_user):
    data = {"sub": test_model_user.username}
    token = create_access_token(data)
    payload = decode_access_token(token)
    assert payload["sub"] == test_model_user.username

def test_decode_access_token_expired(db_session, test_model_user):
    data = {"sub": test_model_user.username}
    token = create_access_token(data, expires_delta=timedelta(seconds=-1))
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(token)
    assert exc_info.value.status_code == 401
    assert "Token has expired" in str(exc_info.value.detail)

def test_decode_access_token_invalid(db_session):
    invalid_token = "invalid_token"
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(invalid_token)
    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in str(exc_info.value.detail)

def test_decode_access_token_user_not_found(db_session, test_model_user):
    data = {"sub": test_model_user.username}
    token = create_access_token(data)
    
    # Delete the user from the database
    db_session.delete(test_model_user)
    db_session.commit()
    
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(token)
    assert exc_info.value.status_code == 401
    assert "User not found" in str(exc_info.value.detail)

def test_decode_access_token_revoked(db_session, test_model_user):
    data = {"sub": test_model_user.username}
    
    # Set the token_blacklist_date to a future date
    future_blacklist_date = datetime.now(timezone.utc) + timedelta(seconds=1)
    test_model_user.token_blacklist_date = future_blacklist_date
    db_session.commit()
    
    # Create a token
    token = create_access_token(data)
    
    # Wait for the blacklist date to pass
    import time
    time.sleep(1.1)
    
    # Now try to decode the token
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(token)
    assert exc_info.value.status_code == 401
    assert "Token has been revoked" in str(exc_info.value.detail)

def test_create_access_token_unique_jti(db_session, test_model_user):
    data = {"sub": test_model_user.username}
    token1 = create_access_token(data)
    token2 = create_access_token(data)
    
    payload1 = jwt.decode(token1, settings_core.SECRET_KEY, algorithms=["HS256"])
    payload2 = jwt.decode(token2, settings_core.SECRET_KEY, algorithms=["HS256"])
    
    assert payload1["jti"] != payload2["jti"]
    assert payload1["jti"].replace("-", "").isalnum()  # Verify it's a valid UUID format
    assert payload2["jti"].replace("-", "").isalnum()  # Verify it's a valid UUID format

@patch('backend.app.core.jwt.jwt.decode')
def test_decode_access_token_unexpected_exception(mock_jwt_decode, db_session, test_model_user):
    mock_jwt_decode.side_effect = Exception("Unexpected error")
    
    data = {"sub": test_model_user.username}
    token = create_access_token(data)
    
    with pytest.raises(HTTPException) as exc_info:
        decode_access_token(token)
    assert exc_info.value.status_code == 500
    assert "Internal server error" in str(exc_info.value.detail)
