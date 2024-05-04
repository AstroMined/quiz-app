# filename: tests/test_api_users.py
def test_create_user(client, db_session, random_username):
    data = {
        "username": random_username,
        "password": "TestPassword123!",
        "email": f"{random_username}@example.com"
    }
    response = client.post("/users/", json=data)
    assert response.status_code == 201

def test_read_users(client, db_session, test_user):
    # Authenticate and get the access token
    login_data = {"username": test_user.username, "password": "TestPassword123!"}
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    access_token = response.json()["access_token"]

    # Make the request to the /users/ endpoint with the access token
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/users/", headers=headers)
    assert response.status_code == 200
    assert test_user.username in [user["username"] for user in response.json()]

def test_read_user_me(client, test_user, test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == test_user.username

def test_update_user_me(client, test_user, test_token):
    headers = {"Authorization": f"Bearer {test_token}"}
    updated_data = {"username": "updated_username"}
    response = client.put("/users/me", json=updated_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "updated_username"
