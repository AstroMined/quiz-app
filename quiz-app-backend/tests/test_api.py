# filename: tests/test_api.py
import pytest
from app.schemas.user import UserCreate
from app.crud import crud_user


def test_register_user(client, db_session, random_username):
    user_data = {
        "username": random_username,
        "password": "TestPassword123"
    }
    response = client.post("/register/", json=user_data)
    assert response.status_code == 201

def test_login_user(client, db_session, random_username):
    password = "TestPassword123"
    user_data = UserCreate(username=random_username, password=password)
    crud_user.create_user(db_session, user_data)
    response = client.post("/token", data={"username": random_username, "password": password})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_create_question_set(client):
    question_set_data = {
        "name": "Test Question Set"
    }
    response = client.post("/question-sets/", json=question_set_data)
    assert response.status_code == 201
    assert response.json()["name"] == "Test Question Set"

# Add more API endpoint tests for other routes