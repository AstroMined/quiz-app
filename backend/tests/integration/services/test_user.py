# filename: backend/tests/test_services/test_user_service.py

import pytest
from jose import jwt

from backend.app.core.config import settings_core
from backend.app.services.user_service import get_current_user, oauth2_scheme


def test_oauth2_scheme():
    """
    Test the OAuth2 authentication scheme.
    """
    assert oauth2_scheme.scheme_name == "OAuth2PasswordBearer"
    assert oauth2_scheme.auto_error is True


@pytest.mark.asyncio
async def test_get_current_user_valid(db_session, test_model_user, test_token):
    user, status = await get_current_user(test_token, db_session)

    assert user is not None
    assert user.username == test_model_user.username
    assert status == "valid"


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(db_session):
    invalid_token = "invalid_token"
    user, status = await get_current_user(invalid_token, db_session)

    assert user is None
    assert status == "invalid_token"


@pytest.mark.asyncio
async def test_get_current_user_expired_token(db_session, test_model_user):
    # Create an expired token
    to_encode = {"sub": test_model_user.username, "exp": 1}  # Set expiration to past
    expired_token = jwt.encode(
        to_encode, settings_core.SECRET_KEY, algorithm=settings_core.ALGORITHM
    )

    user, status = await get_current_user(expired_token, db_session)

    assert user is None
    assert status == "token_expired"


@pytest.mark.asyncio
async def test_get_current_user_nonexistent_user(db_session):
    # Create a token for a non-existent user
    to_encode = {"sub": "nonexistent_user"}
    token = jwt.encode(
        to_encode, settings_core.SECRET_KEY, algorithm=settings_core.ALGORITHM
    )

    user, status = await get_current_user(token, db_session)

    assert user is None
    assert status == "user_not_found"


# Note: Testing for internal errors would require mocking, which might be beyond the scope of this test suite.
# If you want to include such a test, you'd need to use a mocking library like unittest.mock or pytest-mock.
