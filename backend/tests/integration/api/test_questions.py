import pytest
from fastapi import HTTPException

from backend.app.core.config import DifficultyLevel
from backend.app.crud.crud_questions import create_question_in_db
from backend.app.models.questions import QuestionModel
from backend.app.schemas.questions import QuestionCreateSchema
from backend.app.services.logging_service import logger


def test_create_question(
    logged_in_client,
    test_model_subject,
    test_model_topic,
    test_model_subtopic,
    test_model_concept,
):
    question_data = {
        "text": "What is the capital of France?",
        "difficulty": DifficultyLevel.EASY.value,
        "subject_ids": [test_model_subject.id],
        "topic_ids": [test_model_topic.id],
        "subtopic_ids": [test_model_subtopic.id],
        "concept_ids": [test_model_concept.id],
    }

    response = logged_in_client.post("/questions/", json=question_data)
    logger.debug(response.json())
    assert response.status_code == 201
    created_question = response.json()
    assert created_question["text"] == "What is the capital of France?"
    assert created_question["difficulty"] == DifficultyLevel.EASY.value


def test_create_question_with_answers(
    logged_in_client,
    test_model_subject,
    test_model_topic,
    test_model_subtopic,
    test_model_concept,
):
    question_data = {
        "text": "What is the largest planet in our solar system?",
        "difficulty": DifficultyLevel.MEDIUM.value,
        "subject_ids": [test_model_subject.id],
        "topic_ids": [test_model_topic.id],
        "subtopic_ids": [test_model_subtopic.id],
        "concept_ids": [test_model_concept.id],
        "answer_choices": [
            {"text": "Jupiter", "is_correct": True},
            {"text": "Saturn", "is_correct": False},
            {"text": "Neptune", "is_correct": False},
            {"text": "Mars", "is_correct": False},
        ],
    }

    response = logged_in_client.post("/questions/with-answers/", json=question_data)
    logger.debug(response.json())
    assert response.status_code == 201
    created_question = response.json()
    logger.debug(created_question)
    assert created_question["text"] == "What is the largest planet in our solar system?"
    assert created_question["difficulty"] == DifficultyLevel.MEDIUM.value
    assert len(created_question["answer_choices"]) == 4
    assert any(
        choice["text"] == "Jupiter" and choice["is_correct"]
        for choice in created_question["answer_choices"]
    )


def test_get_questions(logged_in_client, test_model_questions):
    response = logged_in_client.get("/questions/")
    assert response.status_code == 200
    questions = response.json()
    assert isinstance(questions, list)
    assert len(questions) > 0


def test_get_question(logged_in_client, test_model_questions):
    response = logged_in_client.get(f"/questions/{test_model_questions[0].id}")
    assert response.status_code == 200
    retrieved_question = response.json()
    assert retrieved_question["id"] == test_model_questions[0].id
    assert retrieved_question["text"] == test_model_questions[0].text


def test_update_question(
    logged_in_client,
    test_model_questions,
    test_model_subject,
    test_model_topic,
    test_model_subtopic,
    test_model_concept,
):
    update_data = {
        "text": "Updated question text",
        "difficulty": DifficultyLevel.HARD.value,
        "subject_ids": [test_model_subject.id],
        "topic_ids": [test_model_topic.id],
        "subtopic_ids": [test_model_subtopic.id],
        "concept_ids": [test_model_concept.id],
    }

    response = logged_in_client.patch(
        f"/questions/{test_model_questions[0].id}", json=update_data
    )
    assert response.status_code == 200
    updated_question = response.json()
    assert updated_question["text"] == "Updated question text"
    assert updated_question["difficulty"] == DifficultyLevel.HARD.value


def test_delete_question(logged_in_client, test_model_questions):
    response = logged_in_client.delete(f"/questions/{test_model_questions[0].id}")
    assert response.status_code == 204

    # Verify that the question has been deleted
    get_response = logged_in_client.get(f"/questions/{test_model_questions[0].id}")
    assert get_response.status_code == 404


def test_create_question_unauthorized(
    client,
    test_model_subject,
    test_model_topic,
    test_model_subtopic,
    test_model_concept,
):
    question_data = {
        "text": "Unauthorized question",
        "difficulty": DifficultyLevel.EASY.value,
        "subject_ids": [test_model_subject.id],
        "topic_ids": [test_model_topic.id],
        "subtopic_ids": [test_model_subtopic.id],
        "concept_ids": [test_model_concept.id],
    }
    with pytest.raises(HTTPException) as exc:
        client.post("/questions/", json=question_data)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"


def test_get_questions_unauthorized(client):
    with pytest.raises(HTTPException) as exc:
        client.get("/questions/")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"


def test_get_nonexistent_question(logged_in_client):
    response = logged_in_client.get("/questions/99999")
    assert response.status_code == 404


def test_update_nonexistent_question(
    logged_in_client,
    test_model_subject,
    test_model_topic,
    test_model_subtopic,
    test_model_concept,
):
    update_data = {
        "text": "Nonexistent question",
        "difficulty": DifficultyLevel.EASY.value,
        "subject_ids": [test_model_subject.id],
        "topic_ids": [test_model_topic.id],
        "subtopic_ids": [test_model_subtopic.id],
        "concept_ids": [test_model_concept.id],
    }
    response = logged_in_client.patch("/questions/99999", json=update_data)
    assert response.status_code == 404


def test_delete_nonexistent_question(logged_in_client):
    response = logged_in_client.delete("/questions/99999")
    assert response.status_code == 404


def test_create_question_invalid_data(
    logged_in_client,
    test_model_subject,
    test_model_topic,
    test_model_subtopic,
    test_model_concept,
):
    invalid_question_data = {
        "text": "",  # Empty text
        "difficulty": "INVALID_DIFFICULTY",
        "subject_ids": [test_model_subject.id],
        "topic_ids": [test_model_topic.id],
        "subtopic_ids": [test_model_subtopic.id],
        "concept_ids": [test_model_concept.id],
    }
    response = logged_in_client.post("/questions/", json=invalid_question_data)
    assert response.status_code == 422


def test_create_question_with_invalid_answers(
    logged_in_client,
    test_model_subject,
    test_model_topic,
    test_model_subtopic,
    test_model_concept,
):
    invalid_question_data = {
        "text": "Valid question text",
        "difficulty": DifficultyLevel.EASY.value,
        "subject_ids": [test_model_subject.id],
        "topic_ids": [test_model_topic.id],
        "subtopic_ids": [test_model_subtopic.id],
        "concept_ids": [test_model_concept.id],
        "answer_choices": [
            {"text": "", "is_correct": True},  # Empty answer text
            {"text": "Valid answer", "is_correct": False},
        ],
    }
    response = logged_in_client.post(
        "/questions/with-answers/", json=invalid_question_data
    )
    assert response.status_code == 422


def test_update_question_invalid_data(logged_in_client, test_model_questions):
    invalid_update_data = {"text": "", "difficulty": "INVALID_DIFFICULTY"}  # Empty text
    response = logged_in_client.patch(
        f"/questions/{test_model_questions[0].id}", json=invalid_update_data
    )
    assert response.status_code == 422


def test_get_questions_pagination(
    logged_in_client,
    db_session,
    test_model_subject,
    test_model_topic,
    test_model_subtopic,
    test_model_concept,
):
    # Create 15 questions
    for i in range(15):
        question_data = QuestionCreateSchema(
            text=f"Question {i}",
            difficulty=DifficultyLevel.EASY,
            subject_ids=[test_model_subject.id],
            topic_ids=[test_model_topic.id],
            subtopic_ids=[test_model_subtopic.id],
            concept_ids=[test_model_concept.id],
        )
        create_question_in_db(db_session, question_data.model_dump())

    # Test first page
    response = logged_in_client.get("/questions/?skip=0&limit=10")
    assert response.status_code == 200
    questions = response.json()
    assert len(questions) == 10

    # Test second page
    response = logged_in_client.get("/questions/?skip=10&limit=10")
    assert response.status_code == 200
    questions = response.json()
    assert len(questions) == 5  # Assuming there were no other questions in the database


def test_update_question_no_changes(logged_in_client, test_model_questions):
    current_question = test_model_questions[0]
    update_data = {
        "text": current_question.text,
        "difficulty": current_question.difficulty.value,
        "subject_ids": [subject.id for subject in current_question.subjects],
        "topic_ids": [topic.id for topic in current_question.topics],
        "subtopic_ids": [subtopic.id for subtopic in current_question.subtopics],
        "concept_ids": [concept.id for concept in current_question.concepts],
    }
    response = logged_in_client.patch(
        f"/questions/{current_question.id}", json=update_data
    )
    assert response.status_code == 200
    updated_question = response.json()
    assert updated_question["id"] == current_question.id
    assert updated_question["text"] == current_question.text
    assert updated_question["difficulty"] == current_question.difficulty.value


def test_create_question_with_invalid_data(logged_in_client):
    invalid_question_data = {
        "text": "",  # Empty text should be invalid
        "subtopic_ids": [],
    }

    response = logged_in_client.post("/questions/", json=invalid_question_data)
    assert response.status_code == 422


def test_create_question_with_answers_invalid_data(logged_in_client):
    invalid_question_data = {
        "text": "Valid question text",
        "subtopic_ids": [1],
        "answer_choices": [
            {"text": "", "is_correct": True},  # Empty answer text should be invalid
            {"text": "Valid answer", "is_correct": False},
        ],
    }

    response = logged_in_client.post(
        "/questions/with-answers/", json=invalid_question_data
    )
    assert response.status_code == 422


def test_update_question_not_found(logged_in_client):
    update_data = {"text": "Updated question text", "subtopic_ids": [1]}
    response = logged_in_client.patch("/questions/99999", json=update_data)
    assert response.status_code == 404


def test_delete_question_not_found(logged_in_client):
    response = logged_in_client.delete("/questions/99999")
    assert response.status_code == 404


def test_get_questions_unauthorized(client):
    with pytest.raises(HTTPException) as exc:
        client.get("/questions/")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"


def test_create_question_unauthorized(client, test_model_subtopic):
    question_data = {
        "text": "Unauthorized question",
        "subtopic_ids": [test_model_subtopic.id],
    }
    with pytest.raises(HTTPException) as exc:
        client.post("/questions/", json=question_data)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"


def test_update_question_unauthorized(client, test_model_questions):
    update_data = {
        "text": "Unauthorized update",
        "subtopic_ids": [test_model_questions[0].subtopics[0].id],
    }
    with pytest.raises(HTTPException) as exc:
        client.patch(f"/questions/{test_model_questions[0].id}", json=update_data)
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"


def test_delete_question_unauthorized(client, test_model_questions):
    with pytest.raises(HTTPException) as exc:
        client.delete(f"/questions/{test_model_questions[0].id}")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Not authenticated"
