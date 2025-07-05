# filename: backend/tests/test_api/test_api_answer_choices.py

import pytest
from fastapi import HTTPException

from backend.app.services.logging_service import logger


def test_create_answer_choice(logged_in_client, test_model_questions):
    answer_choice_data = {
        "text": "Test Answer",
        "is_correct": True,
        "explanation": "Test Explanation",
    }

    response = logged_in_client.post("/answer-choices/", json=answer_choice_data)
    assert response.status_code == 201
    created_answer_choice = response.json()
    logger.debug("Created answer choice: %s", created_answer_choice)
    assert created_answer_choice["text"] == "Test Answer"
    assert created_answer_choice["is_correct"] == True
    assert created_answer_choice["explanation"] == "Test Explanation"


def test_create_answer_choice_with_question(logged_in_client, test_model_questions):
    answer_choice_data = {
        "text": "Test Answer",
        "is_correct": True,
        "explanation": "Test Explanation",
        "question_ids": [test_model_questions[0].id],
    }

    response = logged_in_client.post(
        "/answer-choices/with-question/", json=answer_choice_data
    )
    assert response.status_code == 201
    created_answer_choice = response.json()
    logger.debug("Created answer choice: %s", created_answer_choice)
    assert created_answer_choice["text"] == "Test Answer"
    assert created_answer_choice["is_correct"] == True
    assert created_answer_choice["explanation"] == "Test Explanation"
    assert test_model_questions[0].id == created_answer_choice["questions"][0]["id"]


def test_get_answer_choices(logged_in_client, test_model_answer_choices):
    response = logged_in_client.get("/answer-choices/")
    assert response.status_code == 200
    answer_choices = response.json()
    assert isinstance(answer_choices, list)
    # Should return at least the number of answer choices we created
    assert len(answer_choices) >= len(test_model_answer_choices)
    # Should include our test answer choices (check by text since IDs might vary)
    answer_texts = [ac["text"] for ac in answer_choices]
    for test_choice in test_model_answer_choices:
        assert test_choice.text in answer_texts


def test_get_answer_choice(logged_in_client, test_model_answer_choices):
    response = logged_in_client.get(
        f"/answer-choices/{test_model_answer_choices[0].id}"
    )
    assert response.status_code == 200
    retrieved_answer_choice = response.json()
    assert retrieved_answer_choice["id"] == test_model_answer_choices[0].id
    assert retrieved_answer_choice["text"] == test_model_answer_choices[0].text
    assert (
        retrieved_answer_choice["is_correct"] == test_model_answer_choices[0].is_correct
    )


def test_update_answer_choice(logged_in_client, test_model_answer_choices):
    update_data = {
        "text": "Updated Answer",
        "is_correct": False,
        "explanation": "Updated Explanation",
    }

    response = logged_in_client.put(
        f"/answer-choices/{test_model_answer_choices[0].id}", json=update_data
    )
    assert response.status_code == 200
    updated_answer_choice = response.json()
    assert updated_answer_choice["text"] == "Updated Answer"
    assert updated_answer_choice["is_correct"] == False
    assert updated_answer_choice["explanation"] == "Updated Explanation"


def test_delete_answer_choice(logged_in_client, test_model_answer_choices):
    response = logged_in_client.delete(
        f"/answer-choices/{test_model_answer_choices[0].id}"
    )
    assert response.status_code == 204

    # Verify that the answer choice has been deleted
    get_response = logged_in_client.get(
        f"/answer-choices/{test_model_answer_choices[0].id}"
    )
    assert get_response.status_code == 404


def test_create_answer_choice_unauthorized(client):
    answer_choice_data = {
        "text": "Unauthorized Answer",
        "is_correct": True,
        "explanation": "Unauthorized Explanation",
        "question_id": 1,
    }

    with pytest.raises(HTTPException) as exc_info:
        client.post("/answer-choices/", json=answer_choice_data)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Not authenticated"


def test_get_answer_choices_unauthorized(client):
    with pytest.raises(HTTPException) as exc_info:
        client.get("/answer-choices/")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Not authenticated"


def test_get_nonexistent_answer_choice(logged_in_client):
    response = logged_in_client.get("/answer-choices/99999")
    assert response.status_code == 404


def test_update_nonexistent_answer_choice(logged_in_client):
    update_data = {
        "text": "Nonexistent Answer",
        "is_correct": True,
        "explanation": "Nonexistent Explanation",
        "question_id": 1,
    }
    response = logged_in_client.put("/answer-choices/99999", json=update_data)
    assert response.status_code == 404


def test_delete_nonexistent_answer_choice(logged_in_client):
    response = logged_in_client.delete("/answer-choices/99999")
    assert response.status_code == 404
