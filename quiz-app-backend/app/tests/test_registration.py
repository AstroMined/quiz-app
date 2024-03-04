# filename: test_registration.py
# test_registration.py updated imports
import pytest
from fastapi.testclient import TestClient
# from main import app  # Adjust import based on your project structure
import random
import string
# from .conftest import client, db_session, test_app

#client = TestClient(test_app)

def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=8))

def test_user_registration(client):
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
    # Example: Test with missing username
    response = client.post("/register/", json={"password": "somepassword"})
    assert response.status_code == 422  # Unprocessable Entity

    # Example: Test with short password
    response = client.post("/register/", json={"username": random_lower_string(), "password": "short"})
    assert response.status_code == 422

def test_registration_with_empty_data(client):
    response = client.post("/register/", json={})
    assert response.status_code == 422

# More specific tests can be added as needed to cover all edge cases and validation rules
