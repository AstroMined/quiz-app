# filename: tests/test_jwt.py
import pytest
from app.core import jwt
from datetime import timedelta

@pytest.fixture
def test_data():
    return {"sub": "testuser"}

def test_jwt_token_generation_and_validation(test_data):
    """Test JWT token generation and subsequent validation."""
    # Generate a token
    token = jwt.create_access_token(data=test_data, expires_delta=timedelta(minutes=15))
    assert token is not None, "Failed to generate JWT token."
    
    # Validate the token
    decoded_username = jwt.verify_token(token, credentials_exception=Exception("Invalid token"))
    assert decoded_username == test_data["sub"], "JWT token validation failed. Username mismatch."
