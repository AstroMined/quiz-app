# filename: app/tests/test_registration.py
"""
This module contains tests for user registration.

The tests cover user registration scenarios, including successful registration,
registration with existing username, registration with invalid data, and registration with empty data.
"""

import pytest
from fastapi.testclient import TestClient
import random
import string

def random_lower_string() -> str:
    """
    Generate a random lowercase string of length 8.

    Returns:
        str: The generated random string.
    """
    return "".join(random.choices(string.ascii_lowercase, k=8))

def test_user_registration(client):
    """
    Test successful user registration.

    This test verifies that a user can successfully register with valid data.

    Args:
        client (TestClient): The FastAPI test client.
    """
    username = random_lower_string()
    password = random_lower_string()
    response = client.post(
        "/register/",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == username
    # Add more assertions as needed

def test_registration_with_existing_username(client):
    """
    Test user registration with an existing username.

    This test verifies that user registration fails when using an already registered username.

    Args:
        client (TestClient): The FastAPI test client.
    """
    username = random_lower_string()
    password = random_lower_string()
    # Register once
    client.post("/register/", json={"username": username, "password": password})
    # Attempt to register again with the same username
    response = client.post("/register/", json={"username": username, "password": password})
    assert response.status_code == 400
    assert "detail" in response.json()
    assert response.json()["detail"] == "Username already registered"

def test_registration_with_invalid_data(client):
    """
    Test user registration with invalid data.

    This test verifies that user registration returns an error when invalid data is provided.

    Args:
        client (TestClient): The FastAPI test client.
    """
    # Example: Test with missing username
    response = client.post("/register/", json={"password": "somepassword"})
    assert response.status_code == 422  # Unprocessable Entity

    # Example: Test with short password
    response = client.post("/register/", json={"username": random_lower_string(), "password": "short"})
    assert response.status_code == 422

def test_registration_with_empty_data(client):
    """
    Test user registration with empty data.

    This test verifies that user registration returns an error when empty data is provided.

    Args:
        client (TestClient): The FastAPI test client.
    """
    response = client.post("/register/", json={})
    assert response.status_code == 422

# More specific tests can be added as needed to cover all edge cases and validation rules