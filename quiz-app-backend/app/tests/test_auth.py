# filename: app/tests/test_auth.py
"""
This module contains tests for user authentication.

The tests cover user authentication success and failure scenarios.
"""

import pytest
import random
import string

def random_lower_string() -> str:
    """
    Generate a random lowercase string of length 8.

    Returns:
        str: The generated random string.
    """
    return "".join(random.choices(string.ascii_lowercase, k=8))

def test_authenticate_user_success(test_user, client):
    """
    Test successful user authentication.

    This test verifies that a user can successfully authenticate with valid credentials.

    Args:
        test_user (tuple): A tuple containing the user object and password.
        client (TestClient): The FastAPI test client.
    """
    user, password = test_user  # Unpack the user object and password
    username = user.username
    response = client.post(
        "/token/",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_authenticate_user_failure(client):
    """
    Test failed user authentication.

    This test verifies that user authentication fails with invalid credentials.

    Args:
        client (TestClient): The FastAPI test client.
    """
    username = random_lower_string()
    response = client.post(
        "/token/",
        data={"username": username, "password": "wrong_password"},
    )
    assert response.status_code == 401
    assert "detail" in response.json()
    assert response.json()["detail"] == "Incorrect username or password"

def test_authenticate_user_missing_credentials(client):
    """
    Test user authentication with missing credentials.

    This test verifies that user authentication returns an error when credentials are missing.

    Args:
        client (TestClient): The FastAPI test client.
    """
    response = client.post(
        "/token/",
        data={},
    )
    assert response.status_code == 422  # Unprocessable Entity for missing fields