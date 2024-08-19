# filename: backend/tests/test_api/test_api_groups.py

from backend.app.services.logging_service import logger


def test_create_group(logged_in_client):
    logger.debug("test_create_group - Creating group data")
    group_data = {"name": "Test API Group", "description": "This is an API test group"}
    logger.debug("test_create_group - Sending POST request to /groups with data: %s", group_data)
    response = logged_in_client.post("/groups", json=group_data)
    logger.debug("test_create_group - Response received: %s", response.text)
    assert response.status_code == 200
    assert response.json()["name"] == "Test API Group"
    assert response.json()["description"] == "This is an API test group"

def test_create_group_with_logged_in_client(logged_in_client):
    logger.info("Running test_create_group_with_logged_in_client")
    logger.debug("Creating group data")
    group_data = {"name": "Test Group with Logged In Client", "description": "This is a test group created with logged_in_client"}
    logger.debug("Sending POST request to /groups with data: %s", group_data)
    response = logged_in_client.post("/groups", json=group_data)
    logger.debug("Response received: %s", response.text)
    logger.debug("Response status code: %s", response.status_code)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    data = response.json()
    logger.debug("Response data: %s", data)
    assert data["name"] == "Test Group with Logged In Client"
    assert data["description"] == "This is a test group created with logged_in_client"

def test_create_group_with_manual_auth(client, test_model_user):
    logger.info("Running test_create_group_with_manual_auth")
    logger.debug("Authenticating user")
    login_data = {"username": test_model_user.username, "password": "TestPassword123!"}
    logger.debug("Sending POST request to /login with data: %s", login_data)
    response = client.post("/login", data=login_data)
    logger.debug("Response received: %s", response.text)
    logger.debug("Response status code: %s", response.status_code)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    access_token = response.json()["access_token"]
    logger.debug("Access token retrieved: %s", access_token)

    logger.debug("Creating group data")
    group_data = {"name": "Test Group with Manual Auth", "description": "This is a test group created with manual authentication"}
    headers = {"Authorization": f"Bearer {access_token}"}
    logger.debug("Sending POST request to /groups with data: %s and headers: %s", group_data, headers)
    response = client.post("/groups", json=group_data, headers=headers)
    logger.debug("Response received: %s", response.text)
    logger.debug("Response status code: %s", response.status_code)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    data = response.json()
    logger.debug("Response data: %s", data)
    assert data["name"] == "Test Group with Manual Auth"
    assert data["description"] == "This is a test group created with manual authentication"

def test_get_group(logged_in_client, test_model_group):
    response = logged_in_client.get(f"/groups/{test_model_group.id}")
    assert response.status_code == 200
    assert response.json()["id"] == test_model_group.id
    assert response.json()["name"] == test_model_group.name

def test_update_group(logged_in_client, test_model_group):
    update_data = {"name": "Updated Group Name"}
    response = logged_in_client.put(f"/groups/{test_model_group.id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Group Name"

def test_delete_group(logged_in_client, test_model_group):
    response = logged_in_client.delete(f"/groups/{test_model_group.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Group deleted successfully"

    # Try deleting the group again
    response = logged_in_client.delete(f"/groups/{test_model_group.id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Group not found"

    response = logged_in_client.get(f"/groups/{test_model_group.id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Group not found"

def test_create_group_valid_data(logged_in_client, test_model_user, db_session):
    group_data = {"name": "API Test Group", "description": "This is a test group for testing the API"}
    response = logged_in_client.post("/groups", json=group_data)
    logger.debug("Response received: %s", response.json())
    assert response.status_code == 200
    assert response.json()["name"] == "API Test Group"
    assert response.json()["description"] == "This is a test group for testing the API"

def test_create_group_empty_name(logged_in_client):
    group_data = {"name": "", "description": "This is an API test group"}
    response = logged_in_client.post("/groups", json=group_data)
    logger.debug("Response received: %s", response.json())
    assert response.status_code == 422
    assert "Group name cannot be empty or whitespace" in response.json()["detail"][0]["msg"]

def test_create_group_long_name(logged_in_client, test_model_user, db_session):
    group_data = {"name": "A" * 101, "description": "This is a test group"}
    response = logged_in_client.post("/groups", json=group_data)
    assert response.status_code == 422
    assert "Group name cannot exceed 100 characters" in response.json()["detail"][0]["msg"]

def test_create_group_invalid_name(logged_in_client, test_model_user, db_session):
    group_data = {"name": "Test@Group", "description": "This is a test group"}
    response = logged_in_client.post("/groups", json=group_data)
    assert response.status_code == 422
    assert "Group name can only contain alphanumeric characters, hyphens, underscores, and spaces" in response.json()["detail"][0]["msg"]

def test_create_group_long_description(logged_in_client, test_model_user, db_session):
    group_data = {"name": "Test Group", "description": "A" * 501}
    response = logged_in_client.post("/groups", json=group_data)
    assert response.status_code == 422
    assert "Group description cannot exceed 500 characters" in response.json()["detail"][0]["msg"]

def test_update_group_valid_data(logged_in_client, test_model_user, test_model_group, db_session):
    update_data = {"name": "Updated Test Group", "description": "This is an updated test group"}
    response = logged_in_client.put(f"/groups/{test_model_group.id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Test Group"
    assert response.json()["description"] == "This is an updated test group"

def test_update_group_empty_name(logged_in_client, test_model_user, test_model_group, db_session):
    update_data = {"name": "", "description": "This is an updated test group"}
    response = logged_in_client.put(f"/groups/{test_model_group.id}", json=update_data)
    logger.debug("Response received: %s", response.json())
    assert response.status_code == 422
    assert "Group name cannot be empty or whitespace" in response.json()["detail"][0]["msg"]

def test_update_group_long_name(logged_in_client, test_model_user, test_model_group, db_session):
    update_data = {"name": "A" * 101, "description": "This is an updated test group"}
    response = logged_in_client.put(f"/groups/{test_model_group.id}", json=update_data)
    assert response.status_code == 422
    assert "Group name cannot exceed 100 characters" in response.json()["detail"][0]["msg"]

def test_update_group_invalid_name(logged_in_client, test_model_user, test_model_group, db_session):
    update_data = {"name": "Updated@Test@Group", "description": "This is an updated test group"}
    response = logged_in_client.put(f"/groups/{test_model_group.id}", json=update_data)
    assert response.status_code == 422
    assert "Group name can only contain alphanumeric characters, hyphens, underscores, and spaces" in response.json()["detail"][0]["msg"]

def test_update_group_long_description(logged_in_client, test_model_user, test_model_group, db_session):
    update_data = {"name": "Updated Test Group", "description": "A" * 501}
    response = logged_in_client.put(f"/groups/{test_model_group.id}", json=update_data)
    assert response.status_code == 422
    assert "Group description cannot exceed 500 characters" in response.json()["detail"][0]["msg"]
