# filename: tests/test_api_users.py
def test_create_user(client, db_session, random_username):
    data = {"username": random_username, "password": "testpassword"}
    response = client.post("/users/", json=data)
    assert response.status_code == 201
    assert response.json()["username"] == random_username

def test_read_users(client, db_session, test_user):
    response = client.get("/users/")
    assert response.status_code == 200
    assert test_user.username in [user["username"] for user in response.json()]

# Add more tests for user API endpoints
