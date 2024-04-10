# filename: tests/test_api_questions.py

def test_create_question_endpoint(logged_in_client, test_subject, test_topic, test_subtopic, test_question_set):
    data = {
        "text": "Test Question",
        "subject_id": test_subject.id,
        "topic_id": test_topic.id,
        "subtopic_id": test_subtopic.id,
        "difficulty": "Easy",
        "answer_choices": [
            {"text": "Answer 1", "is_correct": True},
            {"text": "Answer 2", "is_correct": False}
        ],
        "explanation": "Test Explanation",
        "question_set_ids": [test_question_set.id]
    }
    response = logged_in_client.post("/question/", json=data)
    assert response.status_code == 201

def test_read_questions_without_token(client, db_session, test_question):
    response = client.get("/questions/")
    assert response.status_code == 401

def test_read_questions_with_token(logged_in_client, db_session, test_question):
    response = logged_in_client.get("/questions/")
    assert response.status_code == 200
    questions = response.json()
    found_test_question = next((q for q in questions if q["id"] == test_question.id), None)

    # Now we assert that our test question is indeed found and has the correct data
    assert found_test_question is not None, "Test question was not found in the response."
    assert found_test_question["id"] == test_question.id
    assert found_test_question["text"] == test_question.text
    assert found_test_question["subject_id"] == test_question.subject_id
    assert found_test_question["subtopic_id"] == test_question.subtopic_id
    assert found_test_question["topic_id"] == test_question.topic_id
    assert found_test_question["difficulty"] == test_question.difficulty
    assert found_test_question["explanation"] == test_question.explanation

def test_update_question_not_found(logged_in_client, db_session):
    question_id = 999  # Assuming this ID does not exist
    question_update = {"text": "Updated Question"}
    response = logged_in_client.put(f"/question/{question_id}", json=question_update)
    assert response.status_code == 404
    assert response.json()["detail"] == f"Question with ID {question_id} not found"

def test_delete_question_not_found(logged_in_client, db_session):
    question_id = 999  # Assuming this ID does not exist
    response = logged_in_client.delete(f"/question/{question_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Question with ID {question_id} not found"

def test_update_question_endpoint(logged_in_client, test_question, test_question_set):
    data = {
        "text": "Updated Question",
        "difficulty": "Medium",
        "explanation": "Updated Explanation",
        "question_set_ids": [test_question_set.id]
    }
    response = logged_in_client.put(f"/question/{test_question.id}", json=data)
    assert response.status_code == 200
    assert response.json()["text"] == "Updated Question"
    assert response.json()["difficulty"] == "Medium"
    assert response.json()["explanation"] == "Updated Explanation"
    assert test_question_set.id in response.json()["question_set_ids"]
