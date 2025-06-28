# filename: backend/tests/fixtures/api/auth_fixtures.py

import pytest

from backend.app.core.jwt import create_access_token
from backend.app.services.logging_service import logger


@pytest.fixture(scope="function")
def test_token(test_model_user):
    """Create an access token for the test user."""
    access_token = create_access_token(data={"sub": test_model_user.username})
    return access_token


@pytest.fixture(scope="function")
def logged_in_client(client, test_model_user_with_group):
    """Provide a test client that is already logged in."""
    login_data = {
        "username": test_model_user_with_group.username,
        "password": "TestPassword123!",
    }
    response = client.post("/login", json=login_data)
    logger.debug(response.json())
    access_token = response.json()["access_token"]
    assert response.status_code == 200, "Authentication failed."

    client.headers.update({"Authorization": f"Bearer {access_token}"})
    return client