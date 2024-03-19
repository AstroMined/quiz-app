# filename: tests/test_api_authentication.py
def test_user_authentication(client, test_user):
    """Test user authentication and token retrieval."""
    response = client.post("/token", data={"username": test_user.username, "password": "TestPassword123"})
    assert response.status_code == 200, "Authentication failed."
    assert "access_token" in response.json(), "Access token missing in response."
    assert response.json()["token_type"] == "bearer", "Incorrect token type."

def test_register_user_success(client):
    user_data = {"username": "new_user", "password": "NewPassword123"}
    response = client.post("/register/", json=user_data)
    assert response.status_code == 201

def test_login_user_success(client, test_user):
    """Test successful user login and token retrieval."""
    login_data = {"username": test_user.username, "password": "TestPassword123"}
    response = client.post("/token", data=login_data)
    assert response.status_code == 200, "User login failed."
    assert "access_token" in response.json(), "Access token missing in login response."

def test_registration_user_exists(client, test_user):
    """Test registration with an existing username."""
    response = client.post("/register/", json={"username": test_user.username, "password": "anotherpassword"})
    assert response.status_code == 422, "Registration should fail for existing username."

def test_token_access_with_invalid_credentials(client):
    """Test token access with invalid credentials."""
    response = client.post("/token", data={"username": "nonexistentuser", "password": "wrongpassword"})
    assert response.status_code == 401, "Token issuance should fail with invalid credentials."

def test_register_user_duplicate(client, test_user):
    """
    Test registration with a username that already exists.
    """
    user_data = {"username": test_user.username, "password": "DuplicatePass123"}
    response = client.post("/register/", json=user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

def test_login_wrong_password(client, test_user):
    """
    Test login with incorrect password.
    """
    login_data = {"username": test_user.username, "password": "wrongpassword"}
    response = client.post("/token", data=login_data)
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

# filename: tests/test_api_authentication.py
def test_login_and_access_protected_endpoint(client, test_user):
    login_data = {"username": test_user.username, "password": "TestPassword123"}
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

def test_access_protected_endpoint_with_invalid_token(client):
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 401

def test_register_user_invalid_password(client):
    """Test registration with an invalid password."""
    user_data = {"username": "newuser", "password": "weak"}
    response = client.post("/register/", json=user_data)
    assert response.status_code == 422
    assert "Password must be at least 8 characters long" in str(response.content)

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