# filename: app/tests/test_user_responses.py
"""
This module contains tests for the user response endpoints.

The tests cover the creation and retrieval of user responses.
"""

import json
from fastapi.testclient import TestClient
from main import app
from app.models.user_responses import UserResponse

client = TestClient(app)

def test_create_user_response(db_session):
    """
    Test creating a new user response.

    This test checks if a user response can be created successfully by sending a POST request
    to the "/user-responses/" endpoint with valid data.

    Args:
        db_session: The database session fixture.
    """
    user_response_data = {
        "user_id": 1,
        "question_id": 1,
        "answer_choice_id": 1,
        "is_correct": True
    }

    response = client.post("/user-responses/", json=user_response_data)
    assert response.status_code == 201
    assert response.json()["user_id"] == 1
    assert response.json()["is_correct"] == True

def test_get_user_responses(db_session):
    """
    Test retrieving user responses.

    This test checks if the user responses can be retrieved successfully by sending a GET request
    to the "/user-responses/" endpoint.

    Args:
        db_session: The database session fixture.
    """
    # Create some user responses in the database
    user_response1 = UserResponse(user_id=1, question_id=1, answer_choice_id=1, is_correct=True)
    user_response2 = UserResponse(user_id=2, question_id=2, answer_choice_id=2, is_correct=False)
    db_session.add_all([user_response1, user_response2])
    db_session.commit()

    response = client.get("/user-responses/")
    assert response.status_code == 200
    assert len(response.json()) == 2