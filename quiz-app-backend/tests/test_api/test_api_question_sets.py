# filename: tests/test_api_question_sets.py

import json
import tempfile

def test_create_question_set_endpoint(logged_in_client):
    data = {"name": "Test Question Set", "is_public": True}
    response = logged_in_client.post("/question-sets/", json=data)
    assert response.status_code == 201
    assert response.json()["name"] == "Test Question Set"
    assert response.json()["is_public"] == True

def test_read_question_sets(logged_in_client, db_session, test_question_set):
    response = logged_in_client.get("/question-sets/")
    assert response.status_code == 200
    assert any(qs["id"] == test_question_set.id and qs["name"] == test_question_set.name for qs in response.json())

def test_update_question_set_not_found(logged_in_client):
    question_set_id = 999
    question_set_update = {"name": "Updated Name"}
    response = logged_in_client.put(f"/question-sets/{question_set_id}", json=question_set_update)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

# def test_delete_question_set_not_found(logged_in_client):
#     """
#     Test deleting a question set that does not exist.
#     """
#     question_set_id = 999
#     response = logged_in_client.delete(f"/question-sets/{question_set_id}")
#     assert response.status_code == 404
#     assert response.json()["detail"] == f"Question set with ID {question_set_id} not found."

# def test_upload_question_set_success(logged_in_client, db_session, test_question):
#     # Prepare valid JSON data
#     json_data = [
#         {
#             "text": test_question.text,
#             "subject_id": test_question.subject_id,
#             "topic_id": test_question.topic_id,
#             "subtopic_id": test_question.subtopic_id,
#             "difficulty": test_question.difficulty,
#             "answer_choices": test_question.answer_choices,
#             "explanation": test_question.explanation,
#             "question_set_id": test_question.question_set_ids
#         }
#     ]
    
#     # Create a temporary file with the JSON data
#     with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
#         json.dump(json_data, temp_file)
#         temp_file.flush()  # Ensure the contents are written to the file
#         response = logged_in_client.post("/upload-questions/",
#                                files={"file": ("question_set.json", open(temp_file.name, 'rb'), "application/json")})
        
#     assert response.status_code == 200
#     assert response.json() == {"message": "Question set uploaded successfully"}

def test_upload_question_set_invalid_json(logged_in_client, db_session):
    # Prepare invalid JSON data
    invalid_json = "{'invalid': 'json'}"

    # Create a temporary file with the invalid JSON data
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
        temp_file.write(invalid_json)
        temp_file.flush()  # Ensure the contents are written to the file
        response = logged_in_client.post("/upload-questions/", files={"file": ("invalid.json", open(temp_file.name, 'rb'), "application/json")})

    assert response.status_code == 400
    assert "Invalid JSON data" in response.json()["detail"]

def test_create_question_set_with_existing_name(logged_in_client, test_question_set, test_subject):
    data = {"name": test_question_set.name, "subject_id": test_subject.id}
    response = logged_in_client.post("/question-sets/", json=data)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_retrieve_question_set_with_questions(logged_in_client, test_question_set, test_question):
    response = logged_in_client.get(f"/question-sets/{test_question_set.id}")
    assert response.status_code == 200
    assert response.json()["id"] == test_question_set.id
    assert response.json()["name"] == test_question_set.name

def test_update_question_set_endpoint(logged_in_client, test_question_set, test_question):
    data = {"name": "Updated Question Set", "question_ids": [test_question.id]}
    response = logged_in_client.put(f"/question-sets/{test_question_set.id}", json=data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Question Set"
    assert test_question.id in response.json()["question_ids"]

def test_delete_question_set(logged_in_client, test_question_set, db_session):
    question_set_id = test_question_set.id
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

def test_create_private_question_set(logged_in_client):
    response = logged_in_client.post("/question-sets/", json={"name": "Test Private Set", "is_public": False})
    assert response.status_code == 201
    assert response.json()["is_public"] == False
