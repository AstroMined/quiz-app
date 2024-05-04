# filename: tests/test_schemas_user.py

import pytest
from app.schemas.user import UserCreateSchema

def test_user_create_schema():
    user_data = {
        "username": "testuser",
        "password": "TestPassword123!",
        "email": "testuser@example.com"
    }
    user_schema = UserCreateSchema(**user_data)
    assert user_schema.username == "testuser"
    assert user_schema.password == "TestPassword123!"
    assert user_schema.email == "testuser@example.com"

def test_user_create_schema_password_validation():
    user_data = {
        "username": "testuser",
        "password": "ValidPassword123!",
        "email": "testuser@example.com"
    }
    user_schema = UserCreateSchema(**user_data)
    assert user_schema.password == "ValidPassword123!"

def test_user_create_schema_password_too_short():
    """
    Test password too short validation in UserCreate schema.
    """
    with pytest.raises(ValueError):
        UserCreateSchema(username="testuser", password="short")

def test_user_create_schema_password_valid():
    """
    Test valid password validation in UserCreate schema.
    """
    user_data = {
        "username": "testuser",
        "password": "ValidPassword123!",
        "email": "testuser@example.com"
    }
    user_schema = UserCreateSchema(**user_data)
    assert user_schema.password == "ValidPassword123!"

def test_user_create_schema_password_missing_digit():
    """
    Test password missing a digit validation in UserCreate schema.
    """
    with pytest.raises(ValueError, match="Password must contain at least one digit"):
        UserCreateSchema(username="testuser", password="NoDigitPassword")

def test_user_create_schema_password_missing_uppercase():
    """
    Test password missing an uppercase letter validation in UserCreate schema.
    """
    with pytest.raises(ValueError, match="Password must contain at least one uppercase letter"):
        UserCreateSchema(username="testuser", password="nouppercasepassword123")

def test_user_create_schema_password_missing_lowercase():
    """
    Test password missing a lowercase letter validation in UserCreate schema.
    """
    with pytest.raises(ValueError, match="Password must contain at least one lowercase letter"):
        UserCreateSchema(username="testuser", password="NOLOWERCASEPASSWORD123")

def test_user_create_schema_password_valid_complexity():
    """
    Test valid password complexity validation in UserCreate schema.
    """
    user_data = {
        "username": "testuser",
        "password": "ValidPassword123!",
        "email": "testuser@example.com"
    }
    user_schema = UserCreateSchema(**user_data)
    assert user_schema.password == "ValidPassword123!"

def test_user_create_schema_username_too_short():
    """
    Test username too short validation in UserCreate schema.
    """
    with pytest.raises(ValueError, match='Username must be at least 3 characters long'):
        UserCreateSchema(username='ab', password='ValidPassword123!')

def test_user_create_schema_username_too_long():
    """
    Test username too long validation in UserCreate schema.
    """
    with pytest.raises(ValueError, match='Username must not exceed 50 characters'):
        UserCreateSchema(username='a' * 51, password='ValidPassword123!')

def test_user_create_schema_username_invalid_characters():
    """
    Test username with invalid characters validation in UserCreate schema.
    """
    with pytest.raises(ValueError, match='Username must contain only alphanumeric characters'):
        UserCreateSchema(username='invalid_username!', password='ValidPassword123!')

def test_user_create_schema_username_valid():
    """
    Test valid username validation in UserCreate schema.
    """
    user_data = {
        "username": "validuser",
        "password": "ValidPassword123!",
        "email": "testuser@example.com"
    }
    user_schema = UserCreateSchema(**user_data)
    assert user_schema.username == "validuser"
