# filename: tests/test_api_user_responses.py

def test_create_user_response_invalid_data(client, db_session):
    """
    Test creating a user response with invalid data.
    """
    invalid_data = {
        "user_id": 999,  # Assuming this user ID does not exist
        "question_id": 999,  # Assuming this question ID does not exist
        "answer_choice_id": 999,  # Assuming this answer choice ID does not exist
        "is_correct": True
    }
    response = client.post("/user-responses/", json=invalid_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid user_id"

def test_update_user_response(logged_in_client, db_session, test_user, test_question, test_answer_choice_1):
    response_data = {"user_id": test_user.id, "question_id": test_question.id, "answer_choice_id": test_answer_choice_1.id, "is_correct": True}
    created_response = logged_in_client.post("/user-responses/", json=response_data).json()
    update_data = {"is_correct": False}
    response = logged_in_client.put(f"/user-responses/{created_response['id']}", json=update_data)
    assert response.status_code == 200
    assert response.json()["is_correct"] is False

def test_delete_user_response(logged_in_client, db_session, test_user, test_question, test_answer_choice_1):
    response_data = {"user_id": test_user.id, "question_id": test_question.id, "answer_choice_id": test_answer_choice_1.id, "is_correct": True}
    created_response = logged_in_client.post("/user-responses/", json=response_data).json()
    response = logged_in_client.delete(f"/user-responses/{created_response['id']}")
    assert response.status_code == 204
    response = logged_in_client.get(f"/user-responses/{created_response['id']}")
    assert response.status_code == 404
