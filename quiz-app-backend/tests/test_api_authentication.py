# filename: tests/test_api_authentication.py

import pytest
from fastapi import HTTPException
from datetime import timedelta
from app.core import create_access_token
from app.models import RevokedTokenModel

def test_user_authentication(client, test_user):
    """Test user authentication and token retrieval."""
    response = client.post("/token", data={"username": test_user.username, "password": "TestPassword123!"})
    assert response.status_code == 200, "Authentication failed."
    assert "access_token" in response.json(), "Access token missing in response."
    assert response.json()["token_type"] == "bearer", "Incorrect token type."

def test_register_user_success(client, db_session):
    user_data = {"username": "new_user", "password": "NewPassword123!"}
    response = client.post("/register/", json=user_data)
    assert response.status_code == 201, "User registration failed"

def test_login_user_success(client, test_user):
    """Test successful user login and token retrieval."""
    login_data = {"username": test_user.username, "password": "TestPassword123!"}
    response = client.post("/token", data=login_data)
    assert response.status_code == 200, "User login failed."
    assert "access_token" in response.json(), "Access token missing in login response."

def test_registration_user_exists(client, test_user):
    response = client.post("/register/", json={"username": test_user.username, "password": "anotherpassword"})
    assert response.status_code == 422, "Registration should fail for existing username."

def test_token_access_with_invalid_credentials(client, db_session):
    """Test token access with invalid credentials."""
    response = client.post("/token", data={"username": "nonexistentuser", "password": "wrongpassword"})
    assert response.status_code == 401, "Token issuance should fail with invalid credentials."

def test_register_user_duplicate(client, test_user):
    """
    Test registration with a username that already exists.
    """
    user_data = {"username": test_user.username, "password": "DuplicatePass123!"}
    response = client.post("/register/", json=user_data)
    assert response.status_code == 422
    assert "already registered" in str(response.content)

def test_login_wrong_password(client, test_user):
    """
    Test login with incorrect password.
    """
    login_data = {"username": test_user.username, "password": "wrongpassword"}
    response = client.post("/token", data=login_data)
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_login_and_access_protected_endpoint(client, test_user):
    login_data = {"username": test_user.username, "password": "TestPassword123!"}
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    access_token = response.json()["access_token"]

    # Access a protected endpoint using the token
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 200

def test_access_protected_endpoint_without_token(client):
    response = client.get("/users/")
    assert response.status_code == 401

def test_access_protected_endpoint_with_invalid_token(client, db_session):
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

def test_register_user_invalid_password(client):
    """Test registration with an invalid password."""
    user_data = {"username": "newuser", "password": "weak"}
    response = client.post("/register/", json=user_data)
    assert response.status_code == 422
    assert "Password must be at least 8 characters long" in response.json()["detail"][0]["msg"]

def test_register_user_missing_digit_in_password(client):
    """Test registration with a password missing a digit."""
    user_data = {"username": "newuser", "password": "NoDigitPassword"}
    response = client.post("/register/", json=user_data)
    assert response.status_code == 422
    assert "Password must contain at least one digit" in str(response.content)

def test_register_user_missing_uppercase_in_password(client):
    """Test registration with a password missing an uppercase letter."""
    user_data = {"username": "newuser", "password": "nouppercasepassword123"}
    response = client.post("/register/", json=user_data)
    assert response.status_code == 422
    assert "Password must contain at least one uppercase letter" in str(response.content)

def test_register_user_missing_lowercase_in_password(client):
    """Test registration with a password missing a lowercase letter."""
    user_data = {"username": "newuser", "password": "NOLOWERCASEPASSWORD123"}
    response = client.post("/register/", json=user_data)
    assert response.status_code == 422
    assert "Password must contain at least one lowercase letter" in str(response.content)

def test_login_success(client, test_user):
    """
    Test successful user login.
    """
    response = client.post("/login", json={"username": test_user.username, "password": "TestPassword123!"})
    assert response.status_code == 200, "Authentication failed."
    assert "access_token" in response.json(), "Access token missing in response."
    assert response.json()["token_type"] == "bearer", "Incorrect token type."

def test_login_invalid_credentials(client, db_session):
    """
    Test login with invalid credentials.
    """
    response = client.post("/login", json={"username": "invalid_user", "password": "invalid_password"})
    assert response.status_code == 401
    assert "Username not found" in response.json()["detail"]

def test_logout_success(client, test_user, test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.post("/logout", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"

def test_login_inactive_user(client, test_user, db_session):
    """
    Test login with an inactive user.
    """
    # Set the user as inactive
    test_user.is_active = False
    db_session.commit()
    
    response = client.post("/login", json={"username": test_user.username, "password": "TestPassword123"})
    assert response.status_code == 401
    assert "inactive" in response.json()["detail"]

def test_login_invalid_token_format(client, db_session):
    headers = {"Authorization": "Bearer invalid_token_format"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"

def test_login_expired_token(client, test_user):
    """
    Test accessing a protected route with an expired token.
    """
    # Create an expired token
    expired_token = create_access_token(data={"sub": test_user.username}, expires_delta=timedelta(minutes=-1)) 
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 401
    assert "Token has expired" in response.json()["detail"]

def test_login_nonexistent_user(client, db_session):
    """
    Test login with a non-existent username.
    """
    login_data = {"username": "nonexistent_user", "password": "password123"}
    response = client.post("/login", json=login_data)
    assert response.status_code == 401
    assert "Username not found" in response.json()["detail"]

def test_logout_revoked_token(client, test_user, test_token, db_session):
    # Revoke the token manually
    revoked_token = RevokedTokenModel(token=test_token)
    db_session.add(revoked_token)
    db_session.commit()

    headers = {"Authorization": f"Bearer {test_token}"}
    with pytest.raises(HTTPException) as exc_info:
        client.post("/logout", headers=headers)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token has been revoked"

def test_protected_endpoint_expired_token(client, test_user, db_session):
    """
    Test accessing a protected endpoint with an expired token after logout.
    """
    # Create an access token with a short expiration time
    access_token_expires = timedelta(minutes=-1)
    access_token = create_access_token(data={"sub": test_user.username}, expires_delta=access_token_expires)

    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 401
    assert "Token has expired" in response.json()["detail"]

def test_login_logout_flow(client, test_user):
    """
    Test the complete login and logout flow.
    """
    # Login
    login_data = {"username": test_user.username, "password": "TestPassword123!"}
    login_response = client.post("/login", json=login_data)
    access_token = login_response.json()["access_token"]
    assert login_response.status_code == 200, "Authentication failed."
    assert "access_token" in login_response.json(), "Access token missing in response."
    assert login_response.json()["token_type"] == "bearer", "Incorrect token type."
    
    # Access a protected endpoint with the token
    headers = {"Authorization": f"Bearer {access_token}"}
    protected_response = client.get("/users/", headers=headers)
    assert protected_response.status_code == 200
    
    # Logout
    logout_response = client.post("/logout", headers=headers)
    assert logout_response.status_code == 200
    
    # Try accessing the protected endpoint again after logout
    with pytest.raises(HTTPException) as exc_info:
        client.get("/users/", headers=headers)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token has been revoked"
