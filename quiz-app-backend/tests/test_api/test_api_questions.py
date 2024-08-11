# filename: tests/test_api_questions.py

import pytest
from fastapi import HTTPException
from app.services.logging_service import logger

def test_create_question_endpoint(logged_in_client, test_model_subject, test_model_topic, test_model_subtopic, test_model_question_set, test_model_concept):
    data = {
        "text": "Test Question",
        "subject": test_model_subject,
        "topic": test_model_topic,
        "subtopic": test_model_subtopic,
        "concept": test_model_concept,
        "difficulty": "Easy",
        "answer_choices": [
            {"text": "Answer 1", "is_correct": True, "explanation": "Answer 1 is correct."},
            {"text": "Answer 2", "is_correct": False, "explanation": "Answer 2 is incorrect."}
        ],
        "question_set_ids": [test_model_question_set.id]
    }
    response = logged_in_client.post("/questions/", json=data)
    assert response.status_code == 201
    created_question = response.json()
    assert created_question["text"] == "Test Question"
    assert created_question["subject"]["id"] == test_model_subject.id
    assert created_question["topic"]["id"] == test_model_topic.id
    assert created_question["subtopic"]["id"] == test_model_subtopic.id
    assert created_question["concept"]["id"] == test_model_concept.id
    assert created_question["difficulty"] == "Easy"
    assert len(created_question["answer_choices"]) == 2
    assert len(created_question["question_sets"]) == 1

def test_read_questions_without_token(client, db_session, test_model_questions):
    with pytest.raises(HTTPException) as exc_info:
        response = client.get("/questions/")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Not authenticated"

def test_read_questions_with_token(
    logged_in_client,
    test_model_questions,
    test_model_subject,
    test_model_topic,
    test_model_subtopic,
    test_model_concept
):
    question_id = test_model_questions[0].id
    response = logged_in_client.get(f"/questions/{question_id}/")
    assert response.status_code == 200
    logger.error("Response: %s", response.json())
    question = response.json()

    # Now we assert that our test question is indeed found and has the correct data
    assert question is not None, "Test question was not found in the response."
    assert question["id"] == test_model_questions[0].id
    assert question["text"] == test_model_questions[0].text
    assert question["subject"] == test_model_subject.name
    assert question["subtopic"] == test_model_subtopic.name
    assert question["topic"] == test_model_topic.name
    assert question["concept"] == test_model_concept.name
    assert question["difficulty"] == test_model_questions[0].difficulty

def test_update_question_not_found(logged_in_client):
    question_id = 999  # Assuming this ID does not exist
    question_update = {"text": "Updated Question"}
    response = logged_in_client.put(f"/questions/{question_id}", json=question_update)
    assert response.status_code == 404
    assert response.json()["detail"] == f"Question with ID {question_id} not found"

def test_delete_question_not_found(logged_in_client):
    question_id = 999  # Assuming this ID does not exist
    response = logged_in_client.delete(f"/questions/{question_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Question with ID {question_id} not found"

def test_update_question_endpoint(logged_in_client, test_model_questions):
    data = {
        "text": "Updated Question",
        "difficulty": "Medium"
    }
    response = logged_in_client.put(f"/questions/{test_model_questions[0].id}", json=data)
    assert response.status_code == 200
    assert response.json()["text"] == "Updated Question"
    assert response.json()["difficulty"] == "Medium"
