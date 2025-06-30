# filename: backend/tests/fixtures/api/auth_fixtures.py

import pytest

from backend.app.core.jwt import create_access_token
from backend.app.services.logging_service import logger


@pytest.fixture(scope="function")
def test_token(test_model_user, db_session):
    """Create an access token for the test user."""
    access_token = create_access_token(data={"sub": test_model_user.username}, db=db_session)
    return access_token


@pytest.fixture(scope="function")
def logged_in_client(client, test_model_user_with_group, db_session):
    """
    Provide a test client that is already logged in.
    
    PERFORMANCE FIX: Uses direct token creation instead of login endpoint to avoid
    potential session mismatch issues and improve test reliability. Falls back to
    login endpoint if direct token creation fails for any reason.
    """
    # Create token directly using the same database session to avoid session mismatch issues
    try:
        # Try direct token creation first (more reliable for tests)
        access_token = create_access_token(data={"sub": test_model_user_with_group.username}, db=db_session)
        client.headers.update({"Authorization": f"Bearer {access_token}"})
        logger.debug(f"Created direct token for user: {test_model_user_with_group.username}")
        return client
    except Exception as e:
        logger.warning(f"Direct token creation failed: {e}, falling back to login endpoint")
        
        # Fallback to login endpoint if direct token creation fails
        login_data = {
            "username": test_model_user_with_group.username,
            "password": "TestPassword123!",
        }
        response = client.post("/login", json=login_data)
        logger.debug(f"Login response: {response.json()}")
        
        if response.status_code != 200:
            raise AssertionError(f"Authentication failed with status {response.status_code}: {response.json()}")
        
        access_token = response.json()["access_token"]
        client.headers.update({"Authorization": f"Bearer {access_token}"})
        return client