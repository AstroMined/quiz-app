# filename: tests/test_schemas_user.py

import pytest
from app.schemas.user import UserCreate

def test_user_create_schema_password_validation():
    """
    Test password validation in UserCreate schema.
    """
    # Test password too short
    with pytest.raises(ValueError):
        UserCreate(username="testuser", password="short")

    # Test password valid
    user_data = {"username": "testuser", "password": "ValidPassword123"}
    user_schema = UserCreate(**user_data)
    assert user_schema.password == "ValidPassword123"

def test_user_create_schema_password_complexity_validation():
    """Test password complexity validation in UserCreate schema."""
    # Test password missing a digit
    with pytest.raises(ValueError, match="Password must contain at least one digit"):
        UserCreate(username="testuser", password="NoDigitPassword")

    # Test password missing an uppercase letter
    with pytest.raises(ValueError, match="Password must contain at least one uppercase letter"):
        UserCreate(username="testuser", password="nouppercasepassword123")

    # Test password missing a lowercase letter
    with pytest.raises(ValueError, match="Password must contain at least one lowercase letter"):
        UserCreate(username="testuser", password="NOLOWERCASEPASSWORD123")

    # Test valid password
    user_data = {"username": "testuser", "password": "ValidPassword123"}
    user_schema = UserCreate(**user_data)
    assert user_schema.password == "ValidPassword123"
