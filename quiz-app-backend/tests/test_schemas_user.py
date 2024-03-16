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
    user_data = {"username": "testuser", "password": "validpassword"}
    user_schema = UserCreate(**user_data)
    assert user_schema.password == "validpassword"
