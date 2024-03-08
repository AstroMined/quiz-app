# filename: app/tests/test_questions.py
"""
This module contains tests for the question endpoints.

The tests cover the creation, retrieval, update, and deletion of questions.
"""

import json
from fastapi.testclient import TestClient
from main import app
from app.models.questions import Question

client = TestClient(app)

def test_create_question(db_session):
    """
    Test creating a new question.

    This test checks if a question can be created successfully by sending a POST request
    to the "/questions/" endpoint with valid data.

    Args:
        db_session: The database session fixture.
    """
    question_data = {
        "text": "What is the capital of France?",
        "answer_choices": [
            {"text": "Paris", "is_correct": True},
            {"text": "London", "is_correct": False},
            {"text": "Berlin", "is_correct": False},
            {"text": "Madrid", "is_correct": False}
        ]
    }

    response = client.post("/questions/", json=question_data)
    assert response.status_code == 201
    assert response.json()["text"] == "What is the capital of France?"

def test_get_questions(db_session):
    """
    Test retrieving questions.

    This test checks if the questions can be retrieved successfully by sending a GET request
    to the "/questions/" endpoint.

    Args:
        db_session: The database session fixture.
    """
    # Create some questions in the database
    question1 = Question(text="Question 1")
    question2 = Question(text="Question 2")
    db_session.add_all([question1, question2])
    db_session.commit()

    response = client.get("/questions/")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_update_question(db_session):
    """
    Test updating a question.

    This test checks if a question can be updated successfully by sending a PUT request
    to the "/questions/{question_id}" endpoint with valid data.

    Args:
        db_session: The database session fixture.
    """
    # Create a question in the database
    question = Question(text="Question")
    db_session.add(question)
    db_session.commit()

    updated_question_data = {
        "text": "Updated Question"
    }

    response = client.put(f"/questions/{question.id}", json=updated_question_data)
    assert response.status_code == 200
    assert response.json()["text"] == "Updated Question"

def test_delete_question(db_session):
    """
    Test deleting a question.

    This test checks if a question can be deleted successfully by sending a DELETE request
    to the "/questions/{question_id}" endpoint.

    Args:
        db_session: The database session fixture.
    """
    # Create a question in the database
    question = Question(text="Question")
    db_session.add(question)
    db_session.commit()

    response = client.delete(f"/questions/{question.id}")
    assert response.status_code == 204
    assert db_session.query(Question).count() == 0