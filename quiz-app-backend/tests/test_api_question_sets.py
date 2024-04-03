# filename: tests/test_api_question_sets.py

import json
import tempfile

def test_create_question_set(client, db_session):
    data = {"name": "Test Create Question Set"}
    response = client.post("/question-sets/", json=data)
    assert response.status_code == 201
    assert response.json()["name"] == "Test Create Question Set"

def test_read_question_sets(client, db_session, test_question_set):
    response = client.get("/question-sets/")
    assert response.status_code == 200
    assert any(qs["id"] == test_question_set.id and qs["name"] == test_question_set.name for qs in response.json())

def test_update_nonexistent_question_set(client, test_user):
    """
    Test updating a question set that does not exist.
    """
    question_set_update = {"name": "Updated Name"}
    response = client.put("/question-sets/99999", json=question_set_update)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_update_question_set_not_found(client, db_session):
    question_set_id = 999
    question_set_update = {"name": "Updated Name"}
    response = client.put(f"/question-sets/{question_set_id}", json=question_set_update)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_delete_question_set_not_found(client, db_session):
    """
    Test deleting a question set that does not exist.
    """
    question_set_id = 999
    response = client.delete(f"/question-sets/{question_set_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Question set with ID {question_set_id} not found."

def test_upload_question_set_success(client, db_session, test_user):
    # Login
    login_data = {"username": test_user.username, "password": "TestPassword123!"}
    login_response = client.post("/login", json=login_data)
    access_token = login_response.json()["access_token"]
    assert login_response.status_code == 200, "Authentication failed."
    assert "access_token" in login_response.json(), "Access token missing in response."
    assert login_response.json()["token_type"] == "bearer", "Incorrect token type."
    
    # Prepare valid JSON data
    json_data = [
        {
            "text": "Question 1",
            "subtopic_id": 1,
            "question_set_id": 1,
            "answer_choices": [
                {"text": "Answer 1", "is_correct": True},
                {"text": "Answer 2", "is_correct": False}
            ],
            "explanation": "Explanation for Question 1"
        },
        {
            "text": "Question 2",
            "subtopic_id": 1,
            "question_set_id": 1,
            "answer_choices": [
                {"text": "Answer 1", "is_correct": False},
                {"text": "Answer 2", "is_correct": True}
            ],
            "explanation": "Explanation for Question 2"
        }
    ]
    
    # Create a temporary file with the JSON data
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
        json.dump(json_data, temp_file)
        temp_file.flush()  # Ensure the contents are written to the file
        # Access a protected endpoint with the token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post("/upload-questions/",
                               files={"file": ("question_set.json", open(temp_file.name, 'rb'), "application/json")},
                               headers=headers)
        
    assert response.status_code == 200
    assert response.json() == {"message": "Question set uploaded successfully"}

def test_upload_question_set_invalid_json(client, test_user):
    # Login
    login_data = {"username": test_user.username, "password": "TestPassword123!"}
    login_response = client.post("/login", json=login_data)
    access_token = login_response.json()["access_token"]

    # Prepare invalid JSON data
    invalid_json = "{'invalid': 'json'}"
    
    # Create a temporary file with the invalid JSON data
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_file:
        temp_file.write(invalid_json)
        temp_file.flush()  # Ensure the contents are written to the file
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post("/upload-questions/", files={"file": ("invalid.json", open(temp_file.name, 'rb'), "application/json")}, headers=headers)
 
    assert response.status_code == 400
    assert "Invalid JSON data" in response.json()["detail"]
