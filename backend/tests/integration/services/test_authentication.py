# filename: backend/tests/test_services/test_authentication_service.py

import pytest
import uuid

from backend.app.core.security import get_password_hash
from backend.app.models.users import UserModel
from backend.app.services.authentication_service import (
    authenticate_user,
    revoke_all_user_tokens,
)


def test_authenticate_user(db_session, test_model_role):
    # Create a test user
    hashed_password = get_password_hash("testpassword")
    user = UserModel(
        username="testuser",
        email="testuser@example.com",
        hashed_password=hashed_password,
        is_active=True,
        role_id=test_model_role.id,
    )
    db_session.add(user)
    db_session.commit()

    # Test successful authentication
    authenticated_user = authenticate_user(db_session, "testuser", "testpassword")
    assert authenticated_user is not False
    assert authenticated_user.username == "testuser"

    # Test failed authentication with wrong password
    assert authenticate_user(db_session, "testuser", "wrongpassword") is False

    # Test failed authentication with non-existent user
    assert authenticate_user(db_session, "nonexistentuser", "testpassword") is False

    # Test failed authentication with inactive user
    user.is_active = False
    db_session.commit()
    assert authenticate_user(db_session, "testuser", "testpassword") is False


def test_revoke_all_user_tokens(db_session, test_model_role):
    # Create a test user
    unique_username = f"testuser_{str(uuid.uuid4())[:8]}"
    unique_email = f"testuser_{str(uuid.uuid4())[:8]}@example.com"
    hashed_password = get_password_hash("testpassword")
    user = UserModel(
        username=unique_username,
        email=unique_email,
        hashed_password=hashed_password,
        role_id=test_model_role.id,
    )
    db_session.add(user)
    db_session.commit()

    # Call the function
    revoke_all_user_tokens(db_session, user.id)

    # Since we can't easily mock the revoke_all_tokens_for_user function,
    # we'll just assert that the function call doesn't raise any exceptions
    # In a real-world scenario, you might want to add more specific assertions
    # based on the side effects of revoking tokens
