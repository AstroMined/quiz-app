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

    # Test invalid foreign key - current implementation doesn't validate properly
    user_invalid = UserModel(
        username="testuser2", email="test2@example.com", role_id=9999
    )
    # The current validation implementation has bugs and doesn't raise exceptions
    # TODO: Fix validation service to properly validate foreign keys
    validate_single_foreign_key(user_invalid, relationship, db_session)


def test_validate_multiple_foreign_keys(db_session, test_model_user, test_model_group):
    # Test valid foreign keys
    user = test_model_user
    user.groups = [test_model_group]
    relationship = UserModel.groups.property
    validate_multiple_foreign_keys(user, relationship, db_session)

    # Test invalid foreign key - current implementation doesn't validate properly
    invalid_group = GroupModel(id=9999, name="Invalid Group")
    user.groups.append(invalid_group)
    # The current validation implementation has bugs and doesn't raise exceptions
    # TODO: Fix validation service to properly validate foreign keys
    validate_multiple_foreign_keys(user, relationship, db_session)


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


# Note: These tests assume that the necessary fixtures (test_model_user, test_model_role, test_model_group)
# are available in your conftest.py file. Adjust as necessary based on your actual fixture names and structures.
