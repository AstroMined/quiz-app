# filename: test_auth.py
import pytest
#from fastapi.testclient import TestClient
#from sqlalchemy.orm import Session
#from app.core.security import get_password_hash
from app.crud.crud_user import create_user
#from app.db.session import SessionLocal
# from app.schemas.user import UserCreate
# from main import app  # Adjust import based on your project structure
import random
import string
# from .conftest import client, test_user #, db_session, test_app

# client = TestClient(test_app)

def random_lower_string() -> str:
    return "".join(random.choices(string.ascii_lowercase, k=8))

# @pytest.fixture(scope="module")
# def test_user(db_session):
#     username = random_lower_string()
#     password = random_lower_string()
#     user_in = UserCreate(username=username, password=password)
#     user = create_user(db=db_session, user=user_in)
#     # Here you might also want to include logic to delete the test user after tests are done
#     return user, password  # Return the user object and the plain password

def test_authenticate_user_success(test_user, client):
    user, password = test_user  # Unpack the user object and password
    username = user.username
    response = client.post(
        "/token/",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_authenticate_user_failure(client):
    username = random_lower_string()
    response = client.post(
        "/token/",
        data={"username": username, "password": "wrong_password"},
    )
    assert response.status_code == 401
    assert "detail" in response.json()
    assert response.json()["detail"] == "Incorrect username or password"

def test_authenticate_user_missing_credentials(client):
    response = client.post(
        "/token/",
        data={},
    )
    assert response.status_code == 422  # Unprocessable Entity for missing fields
