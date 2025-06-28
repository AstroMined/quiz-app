# filename: backend/tests/test_api/test_api_groups.py

import pytest
from fastapi import HTTPException


def test_create_group(logged_in_client):
    group_data = {"name": "Test API Group", "description": "This is an API test group"}
    response = logged_in_client.post("/groups", json=group_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Test API Group"
    assert response.json()["description"] == "This is an API test group"


def test_create_group_with_logged_in_client(logged_in_client):
    group_data = {
        "name": "Test Group with Logged In Client",
        "description": "This is a test group created with logged_in_client",
    }
    response = logged_in_client.post("/groups", json=group_data)
    assert (
        response.status_code == 200
    ), f"Expected status code 200, got {response.status_code}"
    data = response.json()
    assert data["name"] == "Test Group with Logged In Client"
    assert data["description"] == "This is a test group created with logged_in_client"


def test_create_group_with_manual_auth(client, test_model_user):
    login_data = {"username": test_model_user.username, "password": "TestPassword123!"}
    response = client.post("/login", json=login_data)
    assert (
        response.status_code == 200
    ), f"Expected status code 200, got {response.status_code}"
    access_token = response.json()["access_token"]

    group_data = {
        "name": "Test Group with Manual Auth",
        "description": "This is a test group created with manual authentication",
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("/groups", json=group_data, headers=headers)
    assert (
        response.status_code == 200
    ), f"Expected status code 200, got {response.status_code}"
    data = response.json()
    assert data["name"] == "Test Group with Manual Auth"
    assert (
        data["description"] == "This is a test group created with manual authentication"
    )


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
    assert response.status_code == 204

    # Try deleting the group again
    response = logged_in_client.delete(f"/groups/{test_model_group.id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Group not found"

    response = logged_in_client.get(f"/groups/{test_model_group.id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Group not found"


def test_create_group_valid_data(logged_in_client, test_model_user, db_session):
    group_data = {
        "name": "API Test Group",
        "description": "This is a test group for testing the API",
    }
    response = logged_in_client.post("/groups", json=group_data)
    assert response.status_code == 200
    assert response.json()["name"] == "API Test Group"
    assert response.json()["description"] == "This is a test group for testing the API"


def test_create_group_empty_name(logged_in_client):
    group_data = {"name": "", "description": "This is an API test group"}
    response = logged_in_client.post("/groups", json=group_data)
    assert response.status_code == 422
    assert (
        "String should have at least 1 character" in response.json()["detail"][0]["msg"]
    )


def test_create_group_long_name(logged_in_client, test_model_user, db_session):
    group_data = {"name": "A" * 101, "description": "This is a test group"}
    response = logged_in_client.post("/groups", json=group_data)
    assert response.status_code == 422
    assert (
        "String should have at most 100 characters"
        in response.json()["detail"][0]["msg"]
    )


def test_create_group_invalid_name(logged_in_client, test_model_user, db_session):
    group_data = {"name": "Test@Group", "description": "This is a test group"}
    response = logged_in_client.post("/groups", json=group_data)
    assert response.status_code == 422
    assert (
        "Group name can only contain alphanumeric characters, hyphens, underscores, and spaces"
        in response.json()["detail"][0]["msg"]
    )


def test_create_group_long_description(logged_in_client, test_model_user, db_session):
    group_data = {"name": "Test Group", "description": "A" * 501}
    response = logged_in_client.post("/groups", json=group_data)
    assert response.status_code == 422
    assert (
        "String should have at most 500 characters"
        in response.json()["detail"][0]["msg"]
    )


def test_update_group_valid_data(
    logged_in_client, test_model_user, test_model_group, db_session
):
    update_data = {
        "name": "Updated Test Group",
        "description": "This is an updated test group",
    }
    response = logged_in_client.put(f"/groups/{test_model_group.id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Test Group"
    assert response.json()["description"] == "This is an updated test group"


def test_update_group_empty_name(
    logged_in_client, test_model_user, test_model_group, db_session
):
    update_data = {"name": "", "description": "This is an updated test group"}
    response = logged_in_client.put(f"/groups/{test_model_group.id}", json=update_data)
    assert response.status_code == 422
    assert (
        "String should have at least 1 character" in response.json()["detail"][0]["msg"]
    )


def test_update_group_long_name(
    logged_in_client, test_model_user, test_model_group, db_session
):
    update_data = {"name": "A" * 101, "description": "This is an updated test group"}
    response = logged_in_client.put(f"/groups/{test_model_group.id}", json=update_data)
    assert response.status_code == 422
    assert (
        "String should have at most 100 characters"
        in response.json()["detail"][0]["msg"]
    )


def test_update_group_invalid_name(
    logged_in_client, test_model_user, test_model_group, db_session
):
    update_data = {
        "name": "Updated@Test@Group",
        "description": "This is an updated test group",
    }
    response = logged_in_client.put(f"/groups/{test_model_group.id}", json=update_data)
    assert response.status_code == 422
    assert (
        "Group name can only contain alphanumeric characters, hyphens, underscores, and spaces"
        in response.json()["detail"][0]["msg"]
    )


def test_update_group_long_description(
    logged_in_client, test_model_user, test_model_group, db_session
):
    update_data = {"name": "Updated Test Group", "description": "A" * 501}
    response = logged_in_client.put(f"/groups/{test_model_group.id}", json=update_data)
    assert response.status_code == 422
    assert (
        "String should have at most 500 characters"
        in response.json()["detail"][0]["msg"]
    )


def test_get_nonexistent_group(logged_in_client):
    response = logged_in_client.get(
        "/groups/99999"
    )  # Assuming 99999 is a non-existent group ID
    assert response.status_code == 404
    assert response.json()["detail"] == "Group not found"


def test_update_nonexistent_group(logged_in_client):
    update_data = {"name": "Updated Nonexistent Group"}
    response = logged_in_client.put(
        "/groups/99999", json=update_data
    )  # Assuming 99999 is a non-existent group ID
    assert response.status_code == 404
    assert response.json()["detail"] == "Group not found"


def test_delete_nonexistent_group(logged_in_client):
    response = logged_in_client.delete(
        "/groups/99999"
    )  # Assuming 99999 is a non-existent group ID
    assert response.status_code == 404
    assert response.json()["detail"] == "Group not found"


def test_update_group_not_creator(
    logged_in_client, test_model_group, db_session, test_model_role
):
    # Create a new user who is not the creator of the group
    from backend.app.crud.crud_user import create_user_in_db
    from backend.app.schemas.user import UserCreateSchema

    new_user = UserCreateSchema(
        username="newuser",
        email="newuser@example.com",
        password="TestPassword123!",
        role_id=test_model_role.id,
    )
    hashed_password = new_user.create_hashed_password()
    new_user_db = create_user_in_db(
        db_session, {**new_user.model_dump(), "hashed_password": hashed_password}
    )

    # Log in as the new user
    login_data = {"username": "newuser", "password": "TestPassword123!"}
    login_response = logged_in_client.post("/login", json=login_data)
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Try to update the group as the new user
    update_data = {"name": "Updated by Non-Creator"}
    headers = {"Authorization": f"Bearer {access_token}"}
    response = logged_in_client.put(
        f"/groups/{test_model_group.id}", json=update_data, headers=headers
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Only the group creator can update the group"


def test_delete_group_not_creator(
    logged_in_client, test_model_group, db_session, test_model_role
):
    # Create a new user who is not the creator of the group
    from backend.app.crud.crud_user import create_user_in_db
    from backend.app.schemas.user import UserCreateSchema

    new_user = UserCreateSchema(
        username="newuser2",
        email="newuser2@example.com",
        password="TestPassword123!",
        role_id=test_model_role.id,
    )
    hashed_password = new_user.create_hashed_password()
    new_user_db = create_user_in_db(
        db_session, {**new_user.model_dump(), "hashed_password": hashed_password}
    )

    # Log in as the new user
    login_data = {"username": "newuser2", "password": "TestPassword123!"}
    login_response = logged_in_client.post("/login", json=login_data)
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Try to delete the group as the new user
    headers = {"Authorization": f"Bearer {access_token}"}
    response = logged_in_client.delete(
        f"/groups/{test_model_group.id}", headers=headers
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Only the group creator can delete the group"


def test_create_group_unauthorized(client):
    group_data = {"name": "Unauthorized Group", "description": "This should fail"}
    with pytest.raises(HTTPException) as exc:
        client.post("/groups", json=group_data)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"


def test_get_group_unauthorized(client, test_model_group):
    with pytest.raises(HTTPException) as exc:
        client.get(f"/groups/{test_model_group.id}")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"


def test_update_group_partial(logged_in_client, test_model_group):
    update_data = {"name": "Partially Updated Group"}
    response = logged_in_client.put(f"/groups/{test_model_group.id}", json=update_data)
    assert response.status_code == 200
    updated_group = response.json()
    assert updated_group["name"] == "Partially Updated Group"
    assert (
        updated_group["description"] == test_model_group.description
    )  # Description should remain unchanged


def test_create_group_missing_description(logged_in_client):
    group_data = {"name": "Group Without Description"}
    response = logged_in_client.post("/groups", json=group_data)
    assert response.status_code == 200
    created_group = response.json()
    assert created_group["name"] == "Group Without Description"
    assert created_group["description"] is None


def test_update_group_remove_description(logged_in_client, test_model_group):
    update_data = {"description": None}
    response = logged_in_client.put(f"/groups/{test_model_group.id}", json=update_data)
    assert response.status_code == 200
    updated_group = response.json()
    assert updated_group["name"] == test_model_group.name
    assert updated_group["description"] is None
