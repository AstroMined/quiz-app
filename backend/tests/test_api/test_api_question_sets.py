# filename: backend/tests/test_api_question_sets.py

import json
import tempfile

from backend.app.services.logging_service import logger


def test_create_question_set_endpoint(logged_in_client):
    data = {"name": "Test Question Set", "is_public": True}
    
    response = logged_in_client.post("/question-sets/", json=data)
    assert response.status_code == 201
    assert response.json()["name"] == "Test Question Set"
    assert response.json()["is_public"] == True

def test_create_private_question_set(logged_in_client):
    data = {
        "name": "Test Private Set",
        "is_public": False
    }
    response = logged_in_client.post("/question-sets/", json=data)
    print(response.json())
    assert response.status_code == 201
    assert response.json()["is_public"] == False

def test_read_question_sets(logged_in_client, db_session, test_model_question_set):
    response = logged_in_client.get("/question-sets/")
    assert response.status_code == 200
    assert any(qs["id"] == test_model_question_set.id and qs["name"] == test_model_question_set.name for qs in response.json())

def test_update_question_set_not_found(logged_in_client):
    question_set_id = 999
    question_set_update = {"name": "Updated Name"}
    response = logged_in_client.put(f"/question-sets/{question_set_id}", json=question_set_update)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_upload_question_set_success(logged_in_client, db_session, test_question):
    # Prepare valid JSON data
    json_data = [
        {
            "text": test_question.text,
            "subject_id": test_question.subject_id,
            "topic_id": test_question.topic_id,
            "subtopic_id": test_question.subtopic_id,
            "difficulty": test_question.difficulty,
            "answer_choices": [
                {
                    "text": choice.text,
                    "is_correct": choice.is_correct,
                    "explanation": choice.explanation
                }
                for choice in test_question.answer_choices
            ]
        }
    ]

    # Create a temporary file with the JSON data
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
        json.dump(json_data, temp_file)
        temp_file.flush()  # Ensure the contents are written to the file
        response = logged_in_client.post(
            "/upload-questions/",
            data={"question_set_name": "Test Uploaded Question Set"},
            files={"file": ("question_set.json", open(temp_file.name, 'rb'), "application/json")}
        )

    print(response.json())
    assert response.status_code == 200
    assert response.json() == {"message": "Question set uploaded successfully"}

def test_upload_question_set_invalid_json(logged_in_client, db_session):
    # Prepare invalid JSON data
    invalid_json = "{'invalid': 'json'}"

    # Create a temporary file with the invalid JSON data
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
        temp_file.write(invalid_json)
        temp_file.flush()  # Ensure the contents are written to the file
        response = logged_in_client.post(
            "/upload-questions/",
            data={"question_set_name": "Test Uploaded Question Set with Invalid JSON"},
            files={"file": ("invalid.json", open(temp_file.name, 'rb'), "application/json")})

    print(response.json())
    assert response.status_code == 400
    assert "Invalid JSON data" in response.json()["detail"]

def test_create_question_set_with_existing_name(logged_in_client, test_model_question_set):
    logger.debug("test_model_question_set: %s", test_model_question_set)
    data = {
        "name": test_model_question_set.name,
        "is_public": test_model_question_set.is_public,
        "creator_id": test_model_question_set.creator_id
    }
    response = logged_in_client.post("/question-sets/", json=data)
    logger.debug("response: %s", response.json())
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_retrieve_question_set_with_questions(logged_in_client, test_model_question_set):
    response = logged_in_client.get(f"/question-sets/{test_model_question_set.id}")
    assert response.status_code == 200
    assert response.json()["id"] == test_model_question_set.id
    assert response.json()["name"] == test_model_question_set.name

def test_update_question_set_endpoint(logged_in_client, test_model_question_set, test_question):
    data = {"name": "Updated Question Set", "question_ids": [test_question.id]}
    logger.debug("data: %s", data)
    response = logged_in_client.put(f"/question-sets/{test_model_question_set.id}", json=data)
    logger.debug("response: %s", response.json())
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Question Set"
    assert test_question.id in response.json()["question_ids"]

def test_delete_question_set(logged_in_client, test_model_question_set, db_session):
    question_set_id = test_model_question_set.id
    response = logged_in_client.delete(f"/question-sets/{question_set_id}")
    assert response.status_code == 204
    response = logged_in_client.get("/question-sets/")
    question_sets_after_deletion = response.json()
    if isinstance(question_sets_after_deletion, list):
        assert not any(qs['id'] == question_set_id for qs in question_sets_after_deletion), "Question set was not deleted."
    elif isinstance(question_sets_after_deletion, dict) and 'detail' in question_sets_after_deletion:
        assert question_sets_after_deletion['detail'] == 'No question sets found.', "Unexpected response after deletion."
    else:
        raise AssertionError("Unexpected response format after attempting to delete the question set.")

def test_delete_question_set_not_found(logged_in_client):
    question_set_id = 999
    response = logged_in_client.delete(f"/question-sets/{question_set_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Question set with ID {question_set_id} not found."

def test_update_question_set_with_multiple_questions(logged_in_client, db_session, test_model_question_set, test_model_questions):
    test_question_1 = test_model_questions[0]
    test_question_2 = test_model_questions[1]
    data = {"name": "Updated Question Set", "question_ids": [test_question_1.id, test_question_2.id]}
    response = logged_in_client.put(f"/question-sets/{test_model_question_set.id}", json=data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Question Set"
    assert test_question_1.id in response.json()["question_ids"]
    assert test_question_2.id in response.json()["question_ids"]

def test_update_question_set_remove_questions(logged_in_client, db_session, test_model_question_set, test_question):
    data = {"name": "Updated Question Set", "question_ids": []}
    response = logged_in_client.put(f"/question-sets/{test_model_question_set.id}", json=data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Question Set"
    assert len(response.json()["question_ids"]) == 0

def test_update_question_set_invalid_question_ids(logged_in_client, db_session, test_model_question_set):
    data = {"name": "Updated Question Set", "question_ids": [999]}  # Assuming question with ID 999 doesn't exist
    response = logged_in_client.put(f"/question-sets/{test_model_question_set.id}", json=data)
    assert response.status_code == 400
    assert "Invalid question_id" in response.json()["detail"]
