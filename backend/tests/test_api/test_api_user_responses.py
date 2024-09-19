# filename: backend/tests/test_api_user_responses.py

from datetime import datetime, timezone

from backend.app.services.logging_service import logger, sqlalchemy_obj_to_dict


def test_create_user_response_invalid_user(logged_in_client, test_model_questions):
    invalid_data = {
        "user_id": 999,  # Assuming this user ID does not exist
        "question_id": test_model_questions[0].id,
        "answer_choice_id": test_model_questions[0].answer_choices[0].id
    }
    response = logged_in_client.post("/user-responses/", json=invalid_data)
    logger.debug("Response: %s", response.json())
    assert response.status_code == 400

    # Extract the details from the error response
    detail = response.json()["detail"]

    # Check the error messages
    assert "Invalid user_id" in detail

def test_create_user_response_invalid_question(logged_in_client, test_model_user_with_group, test_model_questions):
    invalid_data = {
        "user_id": test_model_user_with_group.id,
        "question_id": 999,  # Assuming this question ID does not exist
        "answer_choice_id": test_model_questions[0].answer_choices[0].id
    }
    response = logged_in_client.post("/user-responses/", json=invalid_data)
    logger.debug("Response: %s", response.json())
    assert response.status_code == 400

    # Extract the details from the error response
    detail = response.json()["detail"]

    # Check the error messages
    assert "Invalid question_id" in detail
    
def test_create_user_response_invalid_answer(logged_in_client, test_model_user_with_group, test_model_questions):
    invalid_data = {
        "user_id": test_model_user_with_group.id,
        "question_id": test_model_questions[0].id,
        "answer_choice_id": 999  # Assuming this answer choice ID does not exist
    }
    response = logged_in_client.post("/user-responses/", json=invalid_data)
    logger.debug("Response: %s", response.json())
    assert response.status_code == 400

    # Extract the details from the error response
    detail = response.json()["detail"]

    # Check the error messages
    assert "Invalid answer_choice_id" in detail

def test_create_and_score_user_response(logged_in_client, test_model_user, test_model_questions):
    logger.debug("test_questions 1: %s", sqlalchemy_obj_to_dict(test_model_questions[0]))
    correct_answer = next(ac for ac in test_model_questions[0].answer_choices if ac.is_correct)
    response_data = {
        "user_id": test_model_user.id,
        "question_id": test_model_questions[0].id,
        "answer_choice_id": correct_answer.id
    }
    create_response = logged_in_client.post("/user-responses/", json=response_data)
    logger.debug("create_response: %s", create_response.json())
    
    assert create_response.status_code == 201, f"Failed to create user response. Status: {create_response.status_code}, Response: {create_response.json()}"
    
    created_response = create_response.json()
    assert 'id' in created_response, f"Response does not contain 'id'. Response: {created_response}"
    assert created_response['is_correct'] is True, f"Response should be scored as correct. Response: {created_response}"

def test_create_and_score_incorrect_user_response(logged_in_client, test_model_user, test_model_questions):
    incorrect_answer = next(ac for ac in test_model_questions[0].answer_choices if not ac.is_correct)
    response_data = {
        "user_id": test_model_user.id,
        "question_id": test_model_questions[0].id,
        "answer_choice_id": incorrect_answer.id
    }
    create_response = logged_in_client.post("/user-responses/", json=response_data)
    logger.debug("create_response: %s", create_response.json())
    
    assert create_response.status_code == 201, f"Failed to create user response. Status: {create_response.status_code}, Response: {create_response.json()}"
    
    created_response = create_response.json()
    assert 'id' in created_response, f"Response does not contain 'id'. Response: {created_response}"
    assert created_response['is_correct'] is False, f"Response should be scored as incorrect. Response: {created_response}"

def test_update_user_response(logged_in_client, test_model_user, test_model_questions):
    correct_answer = next(ac for ac in test_model_questions[0].answer_choices if ac.is_correct)
    response_data = {
        "user_id": test_model_user.id,
        "question_id": test_model_questions[0].id,
        "answer_choice_id": correct_answer.id
    }
    create_response = logged_in_client.post("/user-responses/", json=response_data)
    assert create_response.status_code == 201
    created_response = create_response.json()
    
    update_data = {
        "response_time": 30  # Update response time
    }
    response = logged_in_client.put(
        f"/user-responses/{created_response['id']}", json=update_data)
    logger.debug("Response: %s", response.json())
    assert response.status_code == 200
    assert response.json()["response_time"] == 30
    assert response.json()["is_correct"] is True  # Ensure is_correct remains unchanged

def test_delete_user_response(logged_in_client, test_model_user_with_group, test_model_questions):
    correct_answer = next(ac for ac in test_model_questions[0].answer_choices if ac.is_correct)
    response_data = {
        "user_id": test_model_user_with_group.id,
        "question_id": test_model_questions[0].id,
        "answer_choice_id": correct_answer.id
    }
    created_response = logged_in_client.post(
        "/user-responses/", json=response_data).json()
    response = logged_in_client.delete(
        f"/user-responses/{created_response['id']}")
    assert response.status_code == 204
    response = logged_in_client.get(
        f"/user-responses/{created_response['id']}")
    assert response.status_code == 404

def test_create_user_response_missing_data(logged_in_client, test_model_user, test_model_questions):
    invalid_data = {
        "user_id": test_model_user.id,
        "question_id": test_model_questions[0].id
        # Missing answer_choice_id
    }
    logger.debug("Running POST request to /user-responses/ with missing data")
    response = logged_in_client.post("/user-responses/", json=invalid_data)
    logger.debug("Response: %s", response.json())
    assert response.status_code == 422  # Updated to expect 422 for validation error

    # Extract the details from the error response
    detail = response.json()["detail"]

    # Check the error messages
    assert "Field required" in str(detail)
    assert "answer_choice_id" in str(detail)

def test_get_user_responses_with_filters(logged_in_client, test_model_user, test_model_questions):
    correct_answer = next(ac for ac in test_model_questions[0].answer_choices if ac.is_correct)
    incorrect_answer = next(ac for ac in test_model_questions[0].answer_choices if not ac.is_correct)
    response_data_1 = {
        "user_id": test_model_user.id,
        "question_id": test_model_questions[0].id,
        "answer_choice_id": correct_answer.id
    }
    response_data_2 = {
        "user_id": test_model_user.id,
        "question_id": test_model_questions[0].id,
        "answer_choice_id": incorrect_answer.id
    }
    logged_in_client.post("/user-responses/", json=response_data_1)
    logged_in_client.post("/user-responses/", json=response_data_2)

    response = logged_in_client.get(f"/user-responses/?user_id={test_model_user.id}")
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = logged_in_client.get(
        f"/user-responses/?question_id={test_model_questions[0].id}")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_user_responses_with_pagination(logged_in_client, test_model_user, test_model_questions):
    correct_answer_1 = next(ac for ac in test_model_questions[0].answer_choices if ac.is_correct)
    correct_answer_2 = next(ac for ac in test_model_questions[1].answer_choices if ac.is_correct)
    response_data_1 = {
        "user_id": test_model_user.id,
        "question_id": test_model_questions[0].id,
        "answer_choice_id": correct_answer_1.id
    }
    response_data_2 = {
        "user_id": test_model_user.id,
        "question_id": test_model_questions[1].id,
        "answer_choice_id": correct_answer_2.id
    }
    logged_in_client.post("/user-responses/", json=response_data_1)
    logged_in_client.post("/user-responses/", json=response_data_2)

    response = logged_in_client.get("/user-responses/?skip=0&limit=1")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert isinstance(response.json()[0]['timestamp'], str)

def test_create_and_retrieve_user_response(logged_in_client, test_model_user, test_model_questions):
    correct_answer = next(ac for ac in test_model_questions[0].answer_choices if ac.is_correct)
    response_data = {
        "user_id": test_model_user.id,
        "question_id": test_model_questions[0].id,
        "answer_choice_id": correct_answer.id
    }
    response = logged_in_client.post("/user-responses/", json=response_data)
    assert response.status_code == 201
    created_response = response.json()
    assert created_response["user_id"] == test_model_user.id
    assert created_response["question_id"] == test_model_questions[0].id
    assert created_response["answer_choice_id"] == correct_answer.id
    assert created_response["is_correct"] is True

    retrieve_response = logged_in_client.get(f"/user-responses/{created_response['id']}")
    assert retrieve_response.status_code == 200
    retrieved_response = retrieve_response.json()
    assert retrieved_response["id"] == created_response["id"]
    assert retrieved_response["user_id"] == test_model_user.id
    assert retrieved_response["question_id"] == test_model_questions[0].id
    assert retrieved_response["answer_choice_id"] == correct_answer.id
    assert retrieved_response["is_correct"] is True

def test_update_nonexistent_user_response(logged_in_client, test_model_user_with_group, test_model_questions):
    update_data = {
        "response_time": 30
    }
    response = logged_in_client.put("/user-responses/999", json=update_data)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_delete_nonexistent_user_response(logged_in_client):
    response = logged_in_client.delete("/user-responses/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
