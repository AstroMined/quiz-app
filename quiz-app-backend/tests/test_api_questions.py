# filename: tests/test_api_questions.py

def test_create_question(client, db_session, test_question_set, test_subtopic):
    data = {
        "text": "Test Question",
        "question_set_id": test_question_set.id,
        "subtopic_id": test_subtopic.id,
        "answer_choices": [
            {"text": "Answer 1", "is_correct": True},
            {"text": "Answer 2", "is_correct": False}
        ],
        "explanation": "Test Explanation"
    }
    response = client.post("/questions/", json=data)
    assert response.status_code == 201, response.text

def test_read_questions_without_token(client, db_session, test_question):
    response = client.get("/questions/")
    assert response.status_code == 401

def test_read_questions_with_token(client, db_session, test_question, test_user):
    # Authenticate and get the access token
    login_data = {"username": test_user.username, "password": "TestPassword123!"}
    response = client.post("/token", data=login_data)
    access_token = response.json()["access_token"]
    assert response.status_code == 200, "Authentication failed."
    assert "access_token" in response.json(), "Access token missing in response."
    assert response.json()["token_type"] == "bearer", "Incorrect token type."

    # Make the request to the /questions/ endpoint with the access token
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/questions/", headers=headers)
    assert response.status_code == 200
    # Deserialize the response to find our test question
    questions = response.json()
    found_test_question = next((q for q in questions if q["id"] == test_question.id), None)

    # Now we assert that our test question is indeed found and has the correct data
    assert found_test_question is not None, "Test question was not found in the response."
    assert found_test_question["text"] == test_question.text
    assert found_test_question["question_set_id"] == test_question.question_set_id
    assert found_test_question["subtopic_id"] == test_question.subtopic_id

def test_update_question_not_found(client, db_session):
    """
    Test updating a question that does not exist.
    """
    question_id = 999  # Assuming this ID does not exist
    question_update = {"text": "Updated Question"}
    response = client.put(f"/questions/{question_id}", json=question_update)
    assert response.status_code == 404
    assert response.json()["detail"] == "Question not found"

def test_delete_question_not_found(client, db_session):
    """
    Test deleting a question that does not exist.
    """
    question_id = 999  # Assuming this ID does not exist
    response = client.delete(f"/questions/{question_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Question not found"
