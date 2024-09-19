# filename: backend/tests/test_api/test_api_authentication.py

import time
import pytest
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone

from backend.app.core.jwt import create_access_token, decode_access_token
from backend.app.crud.crud_user import read_user_by_username_from_db, create_user_in_db
from backend.app.core.security import get_password_hash
from backend.app.services.logging_service import logger

def test_login_success(client, test_model_user):
    login_data = {"username": test_model_user.username, "password": "TestPassword123!"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    login_data = {"username": "nonexistent_user", "password": "WrongPassword123!"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

def test_logout_success(logged_in_client):
    response = logged_in_client.post("/logout")
    logger.debug("Response: %s", response.json())
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"

def test_logout_revoked_token(client, test_model_user):
    login_data = {"username": test_model_user.username, "password": "TestPassword123!"}
    login_response = client.post("/login", json=login_data)
    login_token = login_response.json()["access_token"]
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()
    assert login_response.json()["token_type"] == "bearer"

    logged_in_headers = {"Authorization": f"Bearer {login_token}"}
    logged_in_logout_response = client.post("/logout", headers=logged_in_headers)
    assert logged_in_logout_response.status_code == 200
    assert logged_in_logout_response.json()["message"] == "Successfully logged out"

    logged_out_headers = {"Authorization": f"Bearer {login_token}"}
    logged_out_logout_response = client.post("/logout", headers=logged_out_headers)
    assert logged_out_logout_response.status_code == 401
    assert logged_out_logout_response.json()["detail"] == "Token has been revoked"

def test_protected_endpoint_with_valid_token(logged_in_client):
    response = logged_in_client.get("/users/me")
    assert response.status_code == 200

def test_protected_endpoint_with_expired_token(client, test_model_user, monkeypatch):
    from backend.app.core.config import settings_core
    
    # Temporarily set ACCESS_TOKEN_EXPIRE_MINUTES to a very small value
    monkeypatch.setattr(settings_core, 'ACCESS_TOKEN_EXPIRE_MINUTES', 0)
    
    expired_token = create_access_token({"sub": test_model_user.username})
    headers = {"Authorization": f"Bearer {expired_token}"}
    # Introduce a short delay to ensure token is expired
    time.sleep(1)
    response = client.get("/users/me", headers=headers)
    logger.debug("Response: %s", response.json())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Token has expired" in response.json()["detail"]

@pytest.mark.parametrize("endpoint", [
    "/users/",
    "/users/me",
    "/questions/",
    "/question-sets/",
    "/groups/",
    # Add other protected endpoints here
])
def test_protected_endpoints_require_authentication(client, endpoint):
    with pytest.raises(HTTPException) as exc:
        client.get(endpoint)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"

def test_login_inactive_user(client, db_session, test_model_user):
    # Set the user to inactive
    test_model_user.is_active = False
    db_session.commit()

    login_data = {"username": test_model_user.username, "password": "TestPassword123!"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

def test_login_missing_username(client):
    login_data = {"password": "TestPassword123!"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 422
    assert "Field required" in response.json()["detail"][0]["msg"]

def test_login_missing_password(client):
    login_data = {"username": "testuser"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 422
    assert "Field required" in response.json()["detail"][0]["msg"]

def test_logout_invalid_token(client):
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.post("/logout", headers=headers)
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]

def test_logout_missing_token(client):
    with pytest.raises(HTTPException) as exc:
        client.post("/logout")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"

def test_login_case_insensitive_username(client, test_model_user, db_session, test_model_default_role):
    # Test with uppercase username
    login_data = {"username": test_model_user.username.upper(), "password": "TestPassword123!"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

    # Test with lowercase username
    login_data = {"username": test_model_user.username.lower(), "password": "TestPassword123!"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

    # Test with mixed case username
    mixed_case_username = ''.join([c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(test_model_user.username)])
    login_data = {"username": mixed_case_username, "password": "TestPassword123!"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

    # Test user creation with uppercase username
    hashed_password = get_password_hash("TestPassword123!")
    new_user_data = {
        "username": "TESTUSER123",
        "email": "testuser123@example.com",
        "hashed_password": hashed_password,
        "role_id": test_model_default_role.id
    }
    new_user = create_user_in_db(db_session, new_user_data)
    assert new_user.username == "testuser123"  # Check if stored in lowercase

    # Test login with different cases for the new user
    login_data = {"username": "TestUser123", "password": "TestPassword123!"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_logout_already_logged_out(logged_in_client):
    # Logout once
    first_response = logged_in_client.post("/logout")
    assert first_response.status_code == 200

    # Try to logout again with the same token
    second_response = logged_in_client.post("/logout")
    assert second_response.status_code == 401
    assert "Token has been revoked" in second_response.json()["detail"]

# def test_login_rate_limiting(client, test_model_user):
#     login_data = {"username": test_model_user.username, "password": "WrongPassword"}
    
#     # Attempt to login multiple times with wrong password
#     for _ in range(5):
#         response = client.post("/login", json=login_data)
#         assert response.status_code == 401

#     # The next attempt should be rate limited
#     response = client.post("/login", json=login_data)
#     assert response.status_code == 429
#     assert "Too many login attempts" in response.json()["detail"]

def test_logout_token_reuse(logged_in_client):
    # Logout once
    first_response = logged_in_client.post("/logout")
    assert first_response.status_code == 200

    second_response = logged_in_client.get("/users/me")
    assert second_response.status_code == 401
    assert "Token has been revoked" in second_response.json()["detail"]

def test_login_with_remember_me(client, test_model_user):
    login_data = {
        "username": test_model_user.username,
        "password": "TestPassword123!",
        "remember_me": True
    }
    response = client.post("/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    
    # Check if the token has a longer expiration time
    token = response.json()["access_token"]
    decoded_token = decode_access_token(token)
    assert decoded_token["exp"] - decoded_token["iat"] > 29 * 24 * 60 * 60  # More than 29 days
    assert decoded_token["remember_me"] == True

    # Verify the token is valid
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200

def test_login_without_remember_me(client, test_model_user):
    login_data = {
        "username": test_model_user.username,
        "password": "TestPassword123!",
        "remember_me": False
    }
    response = client.post("/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    
    # Check if the token has a standard expiration time
    token = response.json()["access_token"]
    decoded_token = decode_access_token(token)
    assert decoded_token["exp"] - decoded_token["iat"] <= 24 * 60 * 60  # Less than or equal to 24 hours
    assert decoded_token.get("remember_me") == False

    # Verify the token is valid
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200

def test_logout_with_remember_me_token(client, test_model_user):
    # Login with remember_me
    login_data = {
        "username": test_model_user.username,
        "password": "TestPassword123!",
        "remember_me": True
    }
    login_response = client.post("/login", json=login_data)
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Logout
    headers = {"Authorization": f"Bearer {token}"}
    logout_response = client.post("/logout", headers=headers)
    assert logout_response.status_code == 200
    assert logout_response.json()["message"] == "Successfully logged out"

    # Verify the token is no longer valid
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 401
    assert "Token has been revoked" in response.json()["detail"]

def test_logout_all_sessions(logged_in_client, client, test_model_user, db_session):
    # Create multiple sessions for the user
    tokens = []
    for _ in range(3):
        login_data = {"username": test_model_user.username, "password": "TestPassword123!"}
        response = client.post("/login", json=login_data)
        logger.debug("Initial login response: %s", response.json())
        tokens.append(response.json()["access_token"])

    response = logged_in_client.post("/logout/all")
    logger.debug("Logout response: %s", response.json())
    assert response.status_code == 200
    assert "Successfully logged out from all sessions" in response.json()["message"]

    # Check if all tokens are invalidated
    for token in tokens:
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/users/me", headers=headers)
        logger.debug("Response after logout: %s", response.json())
        assert response.status_code == 401, f"Expected 401 Unauthorized when using a revoked token, got {response.status_code}"

    # Check if the user's token_blacklist_date has been updated
    user = read_user_by_username_from_db(db_session, test_model_user.username)
    assert user.token_blacklist_date is not None
    now = datetime.now(timezone.utc)
    
    # Ensure user.token_blacklist_date is offset-aware
    if user.token_blacklist_date.tzinfo is None:
        user.token_blacklist_date = user.token_blacklist_date.replace(tzinfo=timezone.utc)
    
    assert user.token_blacklist_date > now - timedelta(minutes=1)
    assert user.token_blacklist_date <= now

    # Add a small delay to test the grace period
    time.sleep(1.1)  # Sleep for 1.1 seconds to ensure we're past the 1-second grace period

    login_data = {"username": test_model_user.username, "password": "TestPassword123!"}
    login_response = client.post("/login", json=login_data)
    logger.debug("Login response: %s", login_response.json())
    assert login_response.status_code == 200, "Expected successful login after logout all"
    new_token = login_response.json()["access_token"]
    
    # Verify the new token is valid
    headers = {"Authorization": f"Bearer {new_token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200, "Expected 200 OK when using a new token after logout all"
    
    # Verify token contents
    decoded_token = decode_access_token(new_token)
    assert decoded_token["sub"] == test_model_user.username, "New token should contain the correct username"
    assert "exp" in decoded_token, "New token should have an expiration time"
    assert "jti" in decoded_token, "New token should have a JWT ID"
