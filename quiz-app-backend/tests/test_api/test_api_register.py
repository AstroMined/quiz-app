# filename: tests/test_api/test_api_register.py

from app.services.logging_service import logger


def test_register_user_success(client, db_session, test_model_role):
    user_data = {
        "username": "new_user",
        "password": "NewPassword123!",
        "email": "new_user@example.com",
        "role": test_model_role.name
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 201, "User registration failed"

def test_register_user_invalid_password(client):
    """Test registration with an invalid password."""
    user_data = {
        "username": "newuser",
        "password": "weak",
        "email": "newuser@example.com"
    }
    response = client.post("/register", json=user_data)
    logger.debug(response.json())
    assert response.status_code == 422
    assert "Password must be at least 8 characters long" in response.json()["detail"][0]["msg"]

def test_register_user_missing_digit_in_password(client):
    """Test registration with a password missing a digit."""
    user_data = {"username": "newuser", "password": "NoDigitPassword"}
    response = client.post("/register", json=user_data)
    assert response.status_code == 422
    assert "Password must contain at least one digit" in str(response.content)

def test_register_user_missing_uppercase_in_password(client):
    """Test registration with a password missing an uppercase letter."""
    user_data = {"username": "newuser", "password": "nouppercasepassword123"}
    response = client.post("/register", json=user_data)
    assert response.status_code == 422
    assert "Password must contain at least one uppercase letter" in str(response.content)

def test_register_user_missing_lowercase_in_password(client):
    """Test registration with a password missing a lowercase letter."""
    user_data = {"username": "newuser", "password": "NOLOWERCASEPASSWORD123"}
    response = client.post("/register", json=user_data)
    assert response.status_code == 422
    assert "Password must contain at least one lowercase letter" in str(response.content)

def test_register_user_duplicate(client, test_model_user):
    """
    Test registration with a username that already exists.
    """
    user_data = {
        "username": test_model_user.username,
        "password": "DuplicatePass123!",
        "email": test_model_user.email,
        "role": test_model_user.role
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 422
    assert "already registered" in str(response.content)

def test_registration_user_exists(client, test_model_user):
    response = client.post(
        "/register",
        json={
            "username": test_model_user.username,
            "password": "anotherpassword",
            "email": test_model_user.email
        }
    )
    assert response.status_code == 422, "Registration should fail for existing username."