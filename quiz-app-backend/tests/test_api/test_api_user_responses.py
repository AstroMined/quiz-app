# filename: tests/test_api_user_responses.py
# pylint: disable=unused-argument

def test_create_user_response_invalid_data(logged_in_client, db_session):
    """
    Test creating a user response with invalid data.
    """
    invalid_data = {
        "user_id": 999,  # Assuming this user ID does not exist
        "question_id": 999,  # Assuming this question ID does not exist
        "answer_choice_id": 999,  # Assuming this answer choice ID does not exist
        "is_correct": True
    }
    response = logged_in_client.post("/user-responses/", json=invalid_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid user_id"


def test_update_user_response(
    logged_in_client,
    db_session,
    test_user,
    test_question,
    test_answer_choice_1
):
    response_data = {"user_id": test_user.id, "question_id": test_question.id,
                     "answer_choice_id": test_answer_choice_1.id, "is_correct": True}
    created_response = logged_in_client.post(
        "/user-responses/", json=response_data).json()
    update_data = {"is_correct": False}
    response = logged_in_client.put(
        f"/user-responses/{created_response['id']}", json=update_data)
    assert response.status_code == 200
    assert response.json()["is_correct"] is False


def test_delete_user_response(
    logged_in_client,
    db_session,
    test_user,
    test_question,
    test_answer_choice_1
):
    response_data = {"user_id": test_user.id, "question_id": test_question.id,
                     "answer_choice_id": test_answer_choice_1.id, "is_correct": True}
    created_response = logged_in_client.post(
        "/user-responses/", json=response_data).json()
    response = logged_in_client.delete(
        f"/user-responses/{created_response['id']}")
    assert response.status_code == 204
    response = logged_in_client.get(
        f"/user-responses/{created_response['id']}")
    assert response.status_code == 404


def test_create_user_response_missing_data(logged_in_client, db_session):
    invalid_data = {
        "user_id": 1,
        "question_id": 1
        # Missing answer_choice_id
    }
    response = logged_in_client.post("/user-responses/", json=invalid_data)
    assert response.status_code == 422
    assert "answer_choice_id" in response.text


def test_get_user_responses_with_filters(
    logged_in_client,
    db_session,
    test_user,
    test_question,
    test_answer_choice_1,
    test_answer_choice_2
):
    response_data_1 = {
        "user_id": test_user.id,
        "question_id": test_question.id,
        "answer_choice_id": test_answer_choice_1.id,
        "is_correct": True
    }
    response_data_2 = {
        "user_id": test_user.id,
        "question_id": test_question.id,
        "answer_choice_id": test_answer_choice_2.id,
        "is_correct": False
    }
    post_1 = logged_in_client.post("/user-responses/", json=response_data_1)
    assert post_1.status_code == 201

    post_2 = logged_in_client.post("/user-responses/", json=response_data_2)
    assert post_2.status_code == 201

    response = logged_in_client.get(f"/user-responses/?user_id={test_user.id}")
    assert response.status_code == 200
    assert len(response.json()) == 2

    response = logged_in_client.get(
        f"/user-responses/?question_id={test_question.id}")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_user_responses_with_pagination(
    logged_in_client,
    db_session,
    test_user,
    test_question,test_answer_choice_1
):
    response_data_1 = {
        "user_id": test_user.id,
        "question_id": test_question.id,
        "answer_choice_id": test_answer_choice_1.id,
        "is_correct": True
    }
    response_data_2 = {
        "user_id": test_user.id,
        "question_id": test_question.id + 1,
        "answer_choice_id": test_answer_choice_1.id,
        "is_correct": False
    }
    logged_in_client.post("/user-responses/", json=response_data_1)
    logged_in_client.post("/user-responses/", json=response_data_2)

    response = logged_in_client.get("/user-responses/?skip=0&limit=1")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert isinstance(response.json()[0]['timestamp'], str)
