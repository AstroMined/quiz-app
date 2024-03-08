# filename: app/tests/test_auth.py
"""
This module contains tests for user authentication.

The tests cover user authentication success and failure scenarios.
"""

import pytest
import random
import string
from fastapi.testclient import TestClient
from main import app
from app.models.users import User

client = TestClient(app)

def random_lower_string() -> str:
    """
    Generate a random lowercase string of length 8.

    Returns:
        str: The generated random string.
    """
    return "".join(random.choices(string.ascii_lowercase, k=8))

def test_authenticate_user_success(db_session):
    """
    Test successful user authentication.

    This test verifies that a user can successfully authenticate with valid credentials.

    Args:
        db_session: The database session fixture.
    """
    # Create a user in the database
    username = random_lower_string()
    password = random_lower_string()
    user = User(username=username, hashed_password=password)
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/token/",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_authenticate_user_failure(db_session):
    """
    Test failed user authentication.

    This test verifies that user authentication fails with invalid credentials.

    Args:
        db_session: The database session fixture.
    """
    username = random_lower_string()
    password = random_lower_string()

    response = client.post(
        "/token/",
        data={"username": username, "password": password},
    )
    assert response.status_code == 401
    assert "detail" in response.json()
    assert response.json()["detail"] == "Incorrect username or password"

def test_authenticate_user_missing_credentials(db_session):
    """
    Test user authentication with missing credentials.

    This test verifies that user authentication returns an error when credentials are missing.

    Args:
        db_session: The database session fixture.
    """
    response = client.post(
        "/token/",
        data={},
    )
    assert response.status_code == 422  # Unprocessable Entity for missing fields