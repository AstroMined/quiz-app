# filename: backend/tests/test_api/test_api_users.py

import pytest
from fastapi import HTTPException

from backend.app.core.security import get_password_hash
from backend.app.crud.crud_user import create_user_in_db
from backend.app.models.users import UserModel
from backend.app.schemas.user import UserCreateSchema
from backend.app.services.logging_service import logger


def test_create_user(logged_in_client, test_model_role):
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "TestPassword123!",
        "role_id": test_model_role.id,
    }

    response = logged_in_client.post("/users/", json=user_data)
    assert response.status_code == 201
    created_user = response.json()
    assert created_user["username"] == "newuser"
    assert created_user["email"] == "newuser@example.com"
    assert "password" not in created_user


def test_get_users(logged_in_client):
    response = logged_in_client.get("/users/")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) > 0


def test_get_user_me(logged_in_client, test_model_user_with_group):
    response = logged_in_client.get("/users/me")
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["id"] == test_model_user_with_group.id
    assert user_data["username"] == test_model_user_with_group.username
    assert user_data["email"] == test_model_user_with_group.email


def test_update_user_me(logged_in_client, test_model_user_with_group):
    update_data = {"username": "updated_username", "email": "updated@example.com"}

    response = logged_in_client.put("/users/me", json=update_data)
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["username"] == "updated_username"
    assert updated_user["email"] == "updated@example.com"


def test_create_user_unauthorized(client, test_model_role):
    user_data = {
        "username": "unauthorizeduser",
        "email": "unauthorized@example.com",
        "password": "TestPassword123!",
        "role_id": test_model_role.id,
    }
    with pytest.raises(HTTPException) as exc:
        client.post("/users/", json=user_data)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"


def test_get_users_unauthorized(client):
    with pytest.raises(HTTPException) as exc:
        client.get("/users/")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"


def test_get_user_me_unauthorized(client):
    with pytest.raises(HTTPException) as exc:
        client.get("/users/me")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"


def test_update_user_me_unauthorized(client):
    update_data = {
        "username": "unauthorized_update",
        "email": "unauthorized_update@example.com",
    }
    with pytest.raises(HTTPException) as exc:
        client.put("/users/me", json=update_data)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"


def test_create_user_invalid_data(logged_in_client, test_model_role):
    invalid_user_data = {
        "username": "",  # Empty username
        "email": "invalid_email",  # Invalid email format
        "password": "short",  # Short password
        "role_id": test_model_role.id,
    }
    response = logged_in_client.post("/users/", json=invalid_user_data)
    assert response.status_code == 422


def test_update_user_me_invalid_data(logged_in_client):
    invalid_update_data = {
        "username": "",  # Empty username
        "email": "invalid_email",  # Invalid email format
    }
    response = logged_in_client.put("/users/me", json=invalid_update_data)
    assert response.status_code == 422


def test_get_users_pagination(logged_in_client, db_session, test_model_role):
    # Create 15 users
    for i in range(15):
        user_data = UserCreateSchema(
            username=f"testuser{i}",
            email=f"testuser{i}@example.com",
            password="TestPassword123!",
            role_id=test_model_role.id,
        )
        hashed_password = user_data.create_hashed_password()
        create_user_in_db(
            db_session, {**user_data.model_dump(), "hashed_password": hashed_password}
        )

    # Test first page
    response = logged_in_client.get("/users/?skip=0&limit=10")
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 10

    # Test second page
    response = logged_in_client.get("/users/?skip=10&limit=10")
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 6  # logged_in_client user adds 1 to the count


def test_update_user_me_password(logged_in_client, db_session):
    # First, get the current user's information
    me_response = logged_in_client.get("/users/me")
    assert me_response.status_code == 200
    current_user = me_response.json()

    update_data = {"password": "NewTestPassword123!"}
    response = logged_in_client.put("/users/me", json=update_data)
    assert response.status_code == 200
    updated_user = response.json()
    assert "password" not in updated_user

    # Verify that the password has been updated by trying to log in
    login_data = {
        "username": current_user["username"],  # Use the username, not email
        "password": "NewTestPassword123!",
    }
    login_response = logged_in_client.post("/login", json=login_data)
    assert login_response.status_code == 200


def test_update_user_me_no_changes(logged_in_client, test_model_user_with_group):
    update_data = {
        "username": test_model_user_with_group.username,
        "email": test_model_user_with_group.email,
    }
    response = logged_in_client.put("/users/me", json=update_data)
    assert response.status_code == 200
    updated_user = response.json()
    assert (
        updated_user["username"] == test_model_user_with_group.username.lower()
    )  # Username stored as lowercase
    assert updated_user["email"] == test_model_user_with_group.email


def test_create_user_duplicate_username(
    logged_in_client, test_model_user_with_group, test_model_role
):
    user_data = {
        "username": test_model_user_with_group.username,
        "email": "new_email@example.com",
        "password": "TestPassword123!",
        "role_id": test_model_role.id,
    }
    response = logged_in_client.post("/users/", json=user_data)
    logger.debug(response.json())
    assert response.status_code == 400
    assert "Username already exists" in response.json()["detail"]


def test_create_user_duplicate_email(
    logged_in_client, test_model_user_with_group, test_model_role
):
    user_data = {
        "username": "new_username",
        "email": test_model_user_with_group.email,
        "password": "TestPassword123!",
        "role_id": test_model_role.id,
    }
    response = logged_in_client.post("/users/", json=user_data)
    logger.debug(response.json())
    assert response.status_code == 400
    assert "Email already exists" in response.json()["detail"]


def test_update_user_me_partial(logged_in_client, test_model_user_with_group):
    update_data = {"username": "partial_update_username"}
    response = logged_in_client.put("/users/me", json=update_data)
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["username"] == "partial_update_username"
    assert (
        updated_user["email"] == test_model_user_with_group.email
    )  # Email should remain unchanged


def test_update_user_me_invalid_role(logged_in_client):
    update_data = {"role_id": 99999}  # Assuming this role_id doesn't exist
    response = logged_in_client.put("/users/me", json=update_data)
    logger.debug(response.json())
    assert response.status_code == 422


def test_create_user_missing_required_field(logged_in_client, test_model_role):
    user_data = {
        "username": "missingfield",
        "password": "TestPassword123!",
        "role_id": test_model_role.id,
        # Missing email field
    }
    response = logged_in_client.post("/users/", json=user_data)
    assert response.status_code == 422


def test_create_user_invalid_role(logged_in_client):
    user_data = {
        "username": "invalidrole",
        "email": "invalidrole@example.com",
        "password": "TestPassword123!",
        "role_id": 99999,  # Assuming this role_id doesn't exist
    }
    response = logged_in_client.post("/users/", json=user_data)
    assert response.status_code == 422


def test_get_users_empty_db(logged_in_client, db_session):
    # Clear all users from the database
    db_session.query(UserModel).delete()
    db_session.commit()

    response = logged_in_client.get("/users/")
    logger.debug(response.json())
    assert response.status_code == 401
    assert "User not found" in response.json()["detail"]


def test_update_user_me_same_email(logged_in_client, test_model_user_with_group):
    update_data = {"email": test_model_user_with_group.email}  # Same as current email
    response = logged_in_client.put("/users/me", json=update_data)
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["email"] == test_model_user_with_group.email


def test_create_user_password_hashing(logged_in_client, test_model_role, db_session):
    user_data = {
        "username": "hashtest",
        "email": "hashtest@example.com",
        "password": "TestPassword123!",
        "role_id": test_model_role.id,
    }
    response = logged_in_client.post("/users/", json=user_data)
    assert response.status_code == 201
    created_user = response.json()

    # Retrieve the user from the database
    db_user = (
        db_session.query(UserModel).filter(UserModel.id == created_user["id"]).first()
    )
    assert db_user is not None
    assert db_user.hashed_password != user_data["password"]
    assert db_user.hashed_password.startswith("$2b$")  # Check if it's a bcrypt hash


def test_get_users_limit_exceeds_total(logged_in_client, db_session, test_model_role):
    # Create 5 users
    for i in range(5):
        user_data = UserCreateSchema(
            username=f"limituser{i}",
            email=f"limituser{i}@example.com",
            password="TestPassword123!",
            role_id=test_model_role.id,
        )
        hashed_password = user_data.create_hashed_password()
        create_user_in_db(
            db_session, {**user_data.model_dump(), "hashed_password": hashed_password}
        )

    # Try to get more users than exist
    response = logged_in_client.get("/users/?limit=100")
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 6  # 5 created users + 1 logged-in user
