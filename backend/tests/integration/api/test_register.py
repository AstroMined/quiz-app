# filename: backend/tests/test_api/test_api_register.py

from backend.app.crud.crud_roles import delete_role_from_db, read_default_role_from_db
from backend.app.services.logging_service import logger


def test_register_user_success(client, test_model_role):
    user_data = {
        "username": "new_user",
        "password": "NewPassword123!",
        "email": "new_user@example.com",
        "role_id": test_model_role.id,
    }
    response = client.post("/register", json=user_data)
    assert (
        response.status_code == 201
    ), f"User registration failed. Response: {response.json()}"


def test_register_user_invalid_password(client):
    """Test registration with an invalid password."""
    user_data = {
        "username": "newuser",
        "password": "weak",
        "email": "newuser@example.com",
    }
    response = client.post("/register", json=user_data)
    logger.debug(response.json())
    assert response.status_code == 422
    assert (
        "Value should have at least 8 items after validation"
        in response.json()["detail"][0]["msg"]
    )


def test_register_user_missing_digit_in_password(client):
    """Test registration with a password missing a digit."""
    user_data = {
        "username": "newuser",
        "password": "NoDigitPassword!",
        "email": "newuser@example.com",
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 422
    assert (
        "Password must contain at least one digit"
        in response.json()["detail"][0]["msg"]
    )


def test_register_user_missing_uppercase_in_password(client):
    """Test registration with a password missing an uppercase letter."""
    user_data = {
        "username": "newuser",
        "password": "nouppercasepassword123!",
        "email": "newuser@example.com",
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 422
    assert (
        "Password must contain at least one uppercase letter"
        in response.json()["detail"][0]["msg"]
    )


def test_register_user_missing_lowercase_in_password(client):
    """Test registration with a password missing a lowercase letter."""
    user_data = {
        "username": "newuser",
        "password": "NOLOWERCASEPASSWORD123!",
        "email": "newuser@example.com",
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 422
    assert (
        "Password must contain at least one lowercase letter"
        in response.json()["detail"][0]["msg"]
    )


def test_register_user_duplicate(client, test_model_user):
    """
    Test registration with a username that already exists.
    """
    user_data = {
        "username": test_model_user.username,
        "password": "DuplicatePass123!",
        "email": "new_email@example.com",
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]


def test_registration_user_exists(client, test_model_user):
    response = client.post(
        "/register",
        json={
            "username": test_model_user.username,
            "password": "AnotherPassword123!",
            "email": "another_email@example.com",
        },
    )
    assert (
        response.status_code == 400
    ), "Registration should fail for existing username."
    assert "Username already registered" in response.json()["detail"]


def test_register_user_invalid_email(client, test_model_role):
    user_data = {
        "username": "invalid_email_user",
        "password": "ValidPassword123!",
        "email": "invalid_email",
        "role_id": test_model_role.id,
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 422
    assert "value is not a valid email address" in response.json()["detail"][0]["msg"]


def test_register_user_missing_required_field(client, test_model_role):
    user_data = {
        "username": "missing_field_user",
        "password": "ValidPassword123!",
        # Missing email field
        "role_id": test_model_role.id,
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 422
    assert "Field required" in response.json()["detail"][0]["msg"]


def test_register_user_with_default_role(client, db_session, test_model_default_role):
    # Ensure there's a default role in the database
    default_role = read_default_role_from_db(db_session)
    assert default_role == test_model_default_role

    user_data = {
        "username": "default_role_user",
        "password": "ValidPassword123!",
        "email": "default_role_user@example.com",
        # Not specifying role_id
    }
    response = client.post("/register", json=user_data)
    logger.debug(f"Response for default role test: {response.json()}")
    assert (
        response.status_code == 201
    ), f"Expected 201, got {response.status_code}. Response: {response.json()}"
    assert response.json()["role"] == default_role.name


def test_register_user_no_default_role(client, db_session, test_model_default_role):
    # Get default role from the database
    default_role = read_default_role_from_db(db_session)
    assert default_role == test_model_default_role

    # Delete the default role
    delete_role_from_db(db_session, default_role.id)
    assert read_default_role_from_db(db_session) is None

    user_data = {
        "username": "no_default_role_user",
        "password": "ValidPassword123!",
        "email": "no_default_role_user@example.com",
        # Not specifying role_id
    }
    response = client.post("/register", json=user_data)
    logger.debug(f"Response for no default role test: {response.json()}")
    assert (
        response.status_code == 400
    ), f"Expected 400, got {response.status_code}. Response: {response.json()}"
    assert "No role available for user creation" in response.json()["detail"]


def test_register_user_password_hashing(client, test_model_role, db_session):
    user_data = {
        "username": "hashed_password_user",
        "password": "ValidPassword123!",
        "email": "hashed_password_user@example.com",
        "role_id": test_model_role.id,
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 201

    # Verify the password is hashed in the database
    from backend.app.models.users import UserModel

    db_user = (
        db_session.query(UserModel)
        .filter(UserModel.username == "hashed_password_user")
        .first()
    )
    assert db_user is not None
    assert db_user.hashed_password != "ValidPassword123!"
    assert db_user.hashed_password.startswith("$2b$")  # Check if it's a bcrypt hash


def test_register_user_duplicate_email(client, test_model_user, test_model_role):
    user_data = {
        "username": "unique_username",
        "password": "ValidPassword123!",
        "email": test_model_user.email,  # Using an existing email
        "role_id": test_model_role.id,
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


def test_register_user_long_username(client, test_model_role):
    long_username = "a" * 51  # Assuming max length is 50
    user_data = {
        "username": long_username,
        "password": "ValidPassword123!",
        "email": "long_username@example.com",
        "role_id": test_model_role.id,
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 422
    assert (
        "String should have at most 50 characters"
        in response.json()["detail"][0]["msg"]
    )


def test_register_user_special_characters_in_username(client, test_model_role):
    user_data = {
        "username": "special@username",
        "password": "ValidPassword123!",
        "email": "special_username@example.com",
        "role_id": test_model_role.id,
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 422
    assert (
        "Username must contain only alphanumeric characters, hyphens, underscores, and periods"
        in response.json()["detail"][0]["msg"]
    )


def test_register_user_non_existent_role(client):
    user_data = {
        "username": "non_existent_role_user",
        "password": "ValidPassword123!",
        "email": "non_existent_role@example.com",
        "role_id": 9999,  # Assuming this role_id doesn't exist
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 400
    assert "Invalid role_id" in response.json()["detail"]
