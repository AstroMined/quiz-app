# filename: backend/tests/test_api_users.py

from backend.app.services.logging_service import logger


def test_create_user(logged_in_client, random_username):
    username = random_username + "_test_create_user"
    logger.debug("Creating user with username: %s", username)
    data = {
        "username": username,
        "password": "TestPassword123!",
        "email": f"{username}@example.com"
    }
    logger.debug("Creating user with data: %s", data)
    response = logged_in_client.post("/users/", json=data)
    logger.debug("Response: %s", response.json())
    assert response.status_code == 201

def test_read_users(logged_in_client, test_model_user_with_group):
    response = logged_in_client.get("/users/")
    assert response.status_code == 200
    assert test_model_user_with_group.username in [user["username"] for user in response.json()]

def test_read_user_me(logged_in_client, test_model_user_with_group):
    response = logged_in_client.get("/users/me")
    assert response.status_code == 200
    assert response.json()["username"] == test_model_user_with_group.username

def test_update_user_me(logged_in_client, db_session):
    update_data = {
        "username": "new_username",
        "email": "new_email@example.com"
    }
    response = logged_in_client.put("/users/me", json=update_data)
    logger.debug("Response: %s", response.json())
    assert response.status_code == 200

    # Extract the details from the response
    data = response.json()

    # Check the updated data
    assert data["username"] == "new_username"
    assert data["email"] == "new_email@example.com"
