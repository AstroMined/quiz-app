# filename: tests/test_api_questions.py
def test_create_question(client, db_session, test_question_set):
    # Example modification, assuming 'subtopic_id' is required
    data = {
        "text": "Test Question",
        "question_set_id": test_question_set.id,
        "subtopic_id": 1
    }
    response = client.post("/questions/questions/", json=data)
    assert response.status_code == 201, response.text


def test_read_questions(client, db_session, test_question):
    response = client.get("/questions/questions/")
    assert response.status_code == 200

    # Deserialize the response to find our test question
    questions = response.json()
    found_test_question = next((q for q in questions if q["id"] == test_question.id), None)

    # Now we assert that our test question is indeed found
    assert found_test_question is not None, "Test question was not found in the response."
    assert found_test_question["text"] == test_question.text
    assert found_test_question["question_set_id"] == test_question.question_set_id
    assert found_test_question["subtopic_id"] == test_question.subtopic_id
    # Add asserts for other relevant fields to match your schema

# Add more tests for question API endpoints
