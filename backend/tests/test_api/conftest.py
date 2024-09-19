# filename: backend/tests/test_api/conftest.py

import pytest
from backend.app.crud.crud_time_period import read_time_period_from_db
from backend.app.services.logging_service import logger

@pytest.fixture(scope="function")
def time_period_daily(db_session):
    return read_time_period_from_db(db_session, 1)

@pytest.fixture(scope="function")
def time_period_weekly(db_session):
    return read_time_period_from_db(db_session, 7)

@pytest.fixture(scope="function")
def time_period_monthly(db_session):
    return read_time_period_from_db(db_session, 30)

@pytest.fixture(scope="function")
def time_period_yearly(db_session):
    return read_time_period_from_db(db_session, 365)

@pytest.fixture(scope="function")
def test_users(client, test_model_default_role):
    users = []
    for i in range(5):
        user_data = {
            "username": f"testuser{i}",
            "email": f"testuser{i}@example.com",
            "password": "TestPassword123!"
        }
        response = client.post("/register/", json=user_data)
        logger.debug("Response in test_users %s", response.json())
        users.append(response.json())
    logger.debug("Users in test_users fixture %s", users)
    return users
    

@pytest.fixture(scope="function")
def test_questions_with_answers(logged_in_client, test_model_subject, test_model_topic, test_model_subtopic, test_model_concept):
    questions = []
    for i in range(5):
        answer_choices = []
        for j in range(4):
            answer_choice_data = {
                "text": f"Answer Choice {j} for Question {i}",
                "is_correct": j == 0
            }
            answer_choices.append(answer_choice_data)
        question_data = {
            "text": f"Test Question {i}",
            "difficulty": "Easy",
            "subject_ids": [test_model_subject.id],
            "topic_ids": [test_model_topic.id],
            "subtopic_ids": [test_model_subtopic.id],
            "concept_ids": [test_model_concept.id],
            "answer_choices": answer_choices
        }
        response = logged_in_client.post("/questions/with-answers/", json=question_data)
        questions.append(response.json())
    return questions

@pytest.fixture(scope="function")
def test_user_responses(logged_in_client, test_users, test_questions_with_answers):
    user_responses = []
    for user in test_users:
        for question in test_questions_with_answers:
            correct_answer = next((answer for answer in question["answer_choices"] if answer["is_correct"]), None)
            response_data = {
                "user_id": user["id"],
                "question_id": question["id"],
                "answer_choice_id": correct_answer["id"]
            }
            response = logged_in_client.post("/user-responses/", json=response_data)
            logger.debug("Response in create_user_responses %s", response.json())
            user_responses.append(response.json())
    return user_responses

@pytest.fixture(scope="function")
def setup_test_data(test_questions_with_answers, test_user_responses):
    # This fixture ensures all the data is created and can be used as a single dependency in tests
    pass
