# filename: app/tests/test_question_sets.py
"""
This module contains tests for the question set endpoints.

The tests cover the creation, retrieval, update, and deletion of question sets.
"""

import json
from fastapi.testclient import TestClient
from main import app
from app.models.question_sets import QuestionSet

client = TestClient(app)

def test_create_question_set(db_session):
    """
    Test creating a new question set.

    This test checks if a question set can be created successfully by sending a POST request
    to the "/question-sets/" endpoint with valid data.

    Args:
        db_session: The database session fixture.
    """
    question_set_data = {
        "name": "Test Question Set",
        "questions": [
            {
                "text": "What is the capital of France?",
                "answer_choices": [
                    {"text": "Paris", "is_correct": True},
                    {"text": "London", "is_correct": False},
                    {"text": "Berlin", "is_correct": False},
                    {"text": "Madrid", "is_correct": False}
                ]
            }
        ]
    }

    response = client.post("/question-sets/", json=question_set_data)
    assert response.status_code == 201
    assert response.json()["name"] == "Test Question Set"

def test_get_question_sets(db_session):
    """
    Test retrieving question sets.

    This test checks if the question sets can be retrieved successfully by sending a GET request
    to the "/question-sets/" endpoint.

    Args:
        db_session: The database session fixture.
    """
    # Create some question sets in the database
    question_set1 = QuestionSet(name="Question Set 1")
    question_set2 = QuestionSet(name="Question Set 2")
    db_session.add_all([question_set1, question_set2])
    db_session.commit()

    response = client.get("/question-sets/")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_update_question_set(db_session):
    """
    Test updating a question set.

    This test checks if a question set can be updated successfully by sending a PUT request
    to the "/question-sets/{question_set_id}" endpoint with valid data.

    Args:
        db_session: The database session fixture.
    """
    # Create a question set in the database
    question_set = QuestionSet(name="Question Set")
    db_session.add(question_set)
    db_session.commit()

    updated_question_set_data = {
        "name": "Updated Question Set"
    }

    response = client.put(f"/question-sets/{question_set.id}", json=updated_question_set_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Question Set"

def test_delete_question_set(db_session):
    """
    Test deleting a question set.

    This test checks if a question set can be deleted successfully by sending a DELETE request
    to the "/question-sets/{question_set_id}" endpoint.

    Args:
        db_session: The database session fixture.
    """
    # Create a question set in the database
    question_set = QuestionSet(name="Question Set")
    db_session.add(question_set)
    db_session.commit()

    response = client.delete(f"/question-sets/{question_set.id}")
    assert response.status_code == 204
    assert db_session.query(QuestionSet).count() == 0