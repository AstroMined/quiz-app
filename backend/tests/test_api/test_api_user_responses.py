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

def test_update_user_response(logged_in_client, test_model_user, test_model_questions):
    logger.debug("test_questions 1: %s", sqlalchemy_obj_to_dict(test_model_questions[0]))
    response_data = {
        "user_id": test_model_user.id,
        "question_id": test_model_questions[0].id,
        "answer_choice_id": test_model_questions[0].answer_choices[0].id
    }
    created_response = logged_in_client.post(
        "/user-responses/", json=response_data).json()
    update_data = {
        "is_correct": True,
        "user_id": test_model_user.id,
        "question_id": test_model_questions[0].id,
    }
    response = logged_in_client.put(
        f"/user-responses/{created_response['id']}", json=update_data)
    assert response.status_code == 200
    assert response.json()["is_correct"] is True

def test_delete_user_response(logged_in_client, test_model_user_with_group, test_model_questions):
    response_data = {
        "user_id": test_model_user_with_group.id,
        "question_id": test_model_questions[0].id,
        "answer_choice_id": test_model_questions[0].answer_choices[0].id
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
    assert response.status_code == 400

    # Extract the details from the error response
    detail = response.json()["detail"]

    # Check the error messages
    assert "Field required" in detail
    assert "answer_choice_id" in detail

def test_get_user_responses_with_filters(logged_in_client, test_model_user, test_model_questions):
    response_data_1 = {
        "user_id": test_model_user.id,
        "question_id": test_model_questions[0].id,
        "answer_choice_id": test_model_questions[0].answer_choices[0].id,
        "is_correct": True
    }
    response_data_2 = {
        "user_id": test_model_user.id,
        "question_id": test_model_questions[0].id,
        "answer_choice_id": test_model_questions[0].answer_choices[1].id,
        "is_correct": False
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
    response_data_1 = {
        "user_id": test_model_user.id,
        "question_id": test_model_questions[0].id,
        "answer_choice_id": test_model_questions[0].answer_choices[0].id,
        "is_correct": True
    }
    response_data_2 = {
        "user_id": test_model_user.id,
        "question_id": test_model_questions[1].id,
        "answer_choice_id": test_model_questions[1].answer_choices[0].id,
        "is_correct": False
    }
    logged_in_client.post("/user-responses/", json=response_data_1)
    logged_in_client.post("/user-responses/", json=response_data_2)

    response = logged_in_client.get("/user-responses/?skip=0&limit=1")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert isinstance(response.json()[0]['timestamp'], str)

def test_create_and_retrieve_user_response(logged_in_client, test_model_user, test_model_questions):
    response_data = {
        "user_id": test_model_user.id,
        "question_id": test_model_questions[0].id,
        "answer_choice_id": test_model_questions[0].answer_choices[0].id
    }
    response = logged_in_client.post("/user-responses/", json=response_data)
    assert response.status_code == 201
    created_response = response.json()
    assert created_response["user_id"] == test_model_user.id
    assert created_response["question_id"] == test_model_questions[0].id
    assert created_response["answer_choice_id"] == test_model_questions[0].answer_choices[0].id

    retrieve_response = logged_in_client.get(f"/user-responses/{created_response['id']}")
    assert retrieve_response.status_code == 200
    retrieved_response = retrieve_response.json()
    assert retrieved_response["id"] == created_response["id"]
    assert retrieved_response["user_id"] == test_model_user.id
    assert retrieved_response["question_id"] == test_model_questions[0].id
    assert retrieved_response["answer_choice_id"] == test_model_questions[0].answer_choices[0].id

def test_update_nonexistent_user_response(logged_in_client, test_model_user_with_group, test_model_questions):
    update_data = {
        "is_correct": True,
        "user_id": test_model_user_with_group.id,
        "question_id": test_model_questions[0].id,    
    }
    response = logged_in_client.put("/user-responses/999", json=update_data)
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_delete_nonexistent_user_response(logged_in_client):
    response = logged_in_client.delete("/user-responses/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
