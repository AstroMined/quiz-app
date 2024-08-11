# filename: tests/test_schemas_user.py

import pytest
from pydantic import ValidationError
from app.schemas.user import UserCreateSchema, UserUpdateSchema, UserSchema
from app.core.security import verify_password

def test_user_create_schema_valid():
    user_data = {
        "username": "testuser",
        "password": "TestPassword123!",
        "email": "testuser@example.com"
    }
    user_schema = UserCreateSchema(**user_data)
    assert user_schema.username == "testuser"
    assert user_schema.email == "testuser@example.com"
    hashed_password = user_schema.create_hashed_password()
    assert verify_password("TestPassword123!", hashed_password)

def test_user_create_schema_password_validation():
    with pytest.raises(ValidationError) as exc_info:
        UserCreateSchema(username="testuser", password="weak", email="test@example.com")
    assert "Value should have at least 8 items after validation" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        UserCreateSchema(username="testuser", password="nodigits!", email="test@example.com")
    assert "Password must contain at least one digit" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        UserCreateSchema(username="testuser", password="nouppercase123!", email="test@example.com")
    assert "Password must contain at least one uppercase letter" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        UserCreateSchema(username="testuser", password="NOLOWERCASE123!", email="test@example.com")
    assert "Password must contain at least one lowercase letter" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        UserCreateSchema(username="testuser", password="NoSpecialChar123", email="test@example.com")
    assert "Password must contain at least one special character" in str(exc_info.value)

def test_user_create_schema_username_validation():
    with pytest.raises(ValidationError) as exc_info:
        UserCreateSchema(username="ab", password="ValidPass123!", email="test@example.com")
    assert "String should have at least 3 characters" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        UserCreateSchema(username="a" * 51, password="ValidPass123!", email="test@example.com")
    assert "String should have at most 50 characters" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        UserCreateSchema(username="invalid@user", password="ValidPass123!", email="test@example.com")
    assert "Username must contain only alphanumeric characters" in str(exc_info.value)

def test_user_create_schema_email_validation():
    with pytest.raises(ValidationError) as exc_info:
        UserCreateSchema(username="testuser", password="ValidPass123!", email="invalidemail")
    assert "value is not a valid email address" in str(exc_info.value)

def test_user_update_schema():
    update_data = {
        "username": "updateduser",
        "email": "updated@example.com",
        "password": "NewPassword123!"
    }
    update_schema = UserUpdateSchema(**update_data)
    assert update_schema.username == "updateduser"
    assert update_schema.email == "updated@example.com"
    hashed_password = update_schema.create_hashed_password()
    assert verify_password("NewPassword123!", hashed_password)

def test_user_schema(test_model_user):
    user_schema = UserSchema.model_validate(test_model_user)
    assert user_schema.id == test_model_user.id
    assert user_schema.username == test_model_user.username
    assert user_schema.email == test_model_user.email
    assert user_schema.is_active == test_model_user.is_active
    assert user_schema.is_admin == test_model_user.is_admin
    assert user_schema.role == test_model_user.role.name
    assert isinstance(user_schema.groups, list)
    assert isinstance(user_schema.created_groups, list)
    assert isinstance(user_schema.created_question_sets, list)
    assert isinstance(user_schema.responses, list)
    assert isinstance(user_schema.leaderboards, list)
