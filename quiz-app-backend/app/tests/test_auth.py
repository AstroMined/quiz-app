# filename: test_auth.py
import pytest
import random
import string


def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=8))

def test_authenticate_user_success(test_user, client):
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
    username = random_lower_string()
    response = client.post(
        "/token/",
        data={"username": username, "password": "wrong_password"},
    )
    assert response.status_code == 401
    assert "detail" in response.json()
    assert response.json()["detail"] == "Incorrect username or password"

def test_authenticate_user_missing_credentials(client):
    response = client.post(
        "/token/",
        data={},
    )
    assert response.status_code == 422  # Unprocessable Entity for missing fields
