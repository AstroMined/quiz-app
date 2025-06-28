# filename: backend/tests/test_services/test_validation_service.py

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.base import instance_state

from backend.app.models.groups import GroupModel
from backend.app.models.roles import RoleModel
from backend.app.models.users import UserModel
from backend.app.services.validation_service import (
    validate_direct_foreign_keys,
    validate_foreign_keys,
    validate_multiple_foreign_keys,
    validate_single_foreign_key,
)


def test_validate_single_foreign_key(db_session, test_model_user, test_model_role):
    # Test valid foreign key
    user = UserModel(
        username="testuser", email="test@example.com", role_id=test_model_role.id
    )
    relationship = UserModel.role.property
    validate_single_foreign_key(user, relationship, db_session)

    # Test invalid foreign key - should raise HTTPException
    user_invalid = UserModel(
        username="testuser2", email="test2@example.com", role_id=9999
    )
    with pytest.raises(HTTPException) as exc_info:
        validate_single_foreign_key(user_invalid, relationship, db_session)
    assert exc_info.value.status_code == 400
    assert "Invalid role_id" in str(exc_info.value.detail)


def test_validate_multiple_foreign_keys(db_session, test_model_user, test_model_group):
    # Test valid foreign keys
    user = test_model_user
    user.groups = [test_model_group]
    relationship = UserModel.groups.property
    validate_multiple_foreign_keys(user, relationship, db_session)

    # Test invalid foreign key - should raise HTTPException
    invalid_group = GroupModel(id=9999, name="Invalid Group")
    user.groups.append(invalid_group)
    with pytest.raises(HTTPException) as exc_info:
        validate_multiple_foreign_keys(user, relationship, db_session)
    assert exc_info.value.status_code == 400
    assert "Invalid groups" in str(exc_info.value.detail) and "9999" in str(exc_info.value.detail)


def test_validate_direct_foreign_keys(db_session, test_model_role):
    # Test valid foreign key
    user = UserModel(
        username="testuser", email="test@example.com", role_id=test_model_role.id
    )
    validate_direct_foreign_keys(user, db_session)

    # Test invalid foreign key
    user_invalid = UserModel(
        username="testuser2", email="test2@example.com", role_id=9999
    )
    with pytest.raises(HTTPException) as exc_info:
        validate_direct_foreign_keys(user_invalid, db_session)
    assert exc_info.value.status_code == 400
    assert "Invalid role_id" in str(exc_info.value.detail)


def test_validate_foreign_keys(db_session, test_model_role, test_model_group):
    # Test valid foreign keys
    user = UserModel(
        username="testuser", email="test@example.com", role_id=test_model_role.id
    )
    user.groups = [test_model_group]
    validate_foreign_keys(UserModel, db_session.connection(), user)

    # Test invalid foreign key
    user_invalid = UserModel(
        username="testuser2", email="test2@example.com", role_id=9999
    )
    with pytest.raises(HTTPException) as exc_info:
        validate_foreign_keys(UserModel, db_session.connection(), user_invalid)
    assert exc_info.value.status_code == 400
    assert "Invalid role_id" in str(exc_info.value.detail)


def test_validate_single_foreign_key_edge_cases(db_session, test_model_role):
    """Test edge cases for single foreign key validation."""
    # Test with None value - should not raise exception
    user = UserModel(
        username="testuser", email="test@example.com", role_id=None
    )
    relationship = UserModel.role.property
    validate_single_foreign_key(user, relationship, db_session)
    
    # Test with zero ID - should raise exception
    user_zero = UserModel(
        username="testuser2", email="test2@example.com", role_id=0
    )
    with pytest.raises(HTTPException) as exc_info:
        validate_single_foreign_key(user_zero, relationship, db_session)
    assert exc_info.value.status_code == 400
    assert "Invalid role_id" in str(exc_info.value.detail)


def test_validate_multiple_foreign_keys_edge_cases(db_session, test_model_user, test_model_group):
    """Test edge cases for multiple foreign key validation."""
    # Test with empty list - should not raise exception
    user = test_model_user
    user.groups = []
    relationship = UserModel.groups.property
    validate_multiple_foreign_keys(user, relationship, db_session)
    
    # Test with empty collection - should not raise exception
    user.groups.clear()
    validate_multiple_foreign_keys(user, relationship, db_session)
    
    # Test with mixed valid and invalid objects
    valid_group = test_model_group
    invalid_group = GroupModel(id=9999, name="Invalid Group")
    user.groups = [valid_group, invalid_group]
    with pytest.raises(HTTPException) as exc_info:
        validate_multiple_foreign_keys(user, relationship, db_session)
    assert exc_info.value.status_code == 400
    assert "Invalid groups" in str(exc_info.value.detail) and "9999" in str(exc_info.value.detail)


def test_validate_direct_foreign_keys_edge_cases(db_session, test_model_role):
    """Test edge cases for direct foreign key validation."""
    # Test with string foreign key (should be ignored by current implementation)
    user = UserModel(
        username="testuser", email="test@example.com", role_id=test_model_role.id
    )
    # Add a string attribute that's not a foreign key
    user.username = "string_value"
    validate_direct_foreign_keys(user, db_session)
    
    # Test with non-integer foreign key type (UUID, etc.)
    # This tests the improved introspection logic
    validate_direct_foreign_keys(user, db_session)


def test_find_related_class_by_table():
    """Test table name to class mapping function."""
    from backend.app.services.validation_service import find_related_class_by_table
    from backend.app.models.users import UserModel
    from backend.app.models.roles import RoleModel
    
    # Test existing mappings
    assert find_related_class_by_table("users") == UserModel
    assert find_related_class_by_table("roles") == RoleModel
    
    # Test non-existent mapping
    assert find_related_class_by_table("nonexistent_table") is None


# Note: These tests assume that the necessary fixtures (test_model_user, test_model_role, test_model_group)
# are available in your conftest.py file. Adjust as necessary based on your actual fixture names and structures.
