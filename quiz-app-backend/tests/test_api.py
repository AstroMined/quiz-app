# filename: tests/test_api.py
import pytest
from app.schemas.user import UserCreate
from app.models.users import User
from app.crud.crud_user import create_user


def test_register_user(client, db_session, random_username):
    user_data = {
        "username": random_username,
        "password": "testpassword"
    }
    response = client.post("/register/", json=user_data)
    assert response.status_code == 201
    assert response.json()["username"] == random_username

    # Clean up the created user
    db_session.query(User).filter(User.username == random_username).delete()
    db_session.commit()

def test_login_user(client, db_session, random_username):
    password = "testpassword"
    
    # Create a user for testing login
    user_data = UserCreate(username=random_username, password=password)
    create_user(db_session, user_data)
    
    response = client.post("/token", data={"username": random_username, "password": password})
    assert response.status_code == 200
    assert "access_token" in response.json()

    # Clean up the created user
    db_session.query(User).filter(User.username == random_username).delete()
    db_session.commit()

def test_create_question_set(client):
    question_set_data = {
        "name": "Test Question Set"
    }
    response = client.post("/question-sets/", json=question_set_data)
    assert response.status_code == 201
    assert response.json()["name"] == "Test Question Set"

# Add more API endpoint tests for other routes