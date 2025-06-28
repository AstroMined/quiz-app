# filename: backend/tests/fixtures/api/test_data_fixtures.py

import pytest

from backend.app.crud.crud_time_period import read_time_period_from_db
from backend.app.services.logging_service import logger
from backend.app.core.security import get_password_hash


@pytest.fixture(scope="function")
def time_period_daily(db_session):
    """Get the daily time period from the database."""
    return read_time_period_from_db(db_session, 1)


@pytest.fixture(scope="function")
def time_period_weekly(db_session):
    """Get the weekly time period from the database."""
    return read_time_period_from_db(db_session, 7)


@pytest.fixture(scope="function")
def time_period_monthly(db_session):
    """Get the monthly time period from the database."""
    return read_time_period_from_db(db_session, 30)


@pytest.fixture(scope="function")
def time_period_yearly(db_session):
    """Get the yearly time period from the database."""
    return read_time_period_from_db(db_session, 365)


@pytest.fixture(scope="function")
def test_users(client, test_model_default_role):
    """Create multiple test users via API registration."""
    users = []
    for i in range(5):
        user_data = {
            "username": f"testuser{i}",
            "email": f"testuser{i}@example.com",
            "password": "TestPassword123!",
        }
        response = client.post("/register/", json=user_data)
        logger.debug("Response in test_users %s", response.json())
        users.append(response.json())
    logger.debug("Users in test_users fixture %s", users)
    return users


@pytest.fixture(scope="function")
def test_questions_with_answers(
    logged_in_client,
    test_model_subject,
    test_model_topic,
    test_model_subtopic,
    test_model_concept,
):
    """Create multiple test questions with answers via API."""
    questions = []
    for i in range(5):
        answer_choices = []
        for j in range(4):
            answer_choice_data = {
                "text": f"Answer Choice {j} for Question {i}",
                "is_correct": j == 0,
            }
            answer_choices.append(answer_choice_data)
        question_data = {
            "text": f"Test Question {i}",
            "difficulty": "Easy",
            "subject_ids": [test_model_subject.id],
            "topic_ids": [test_model_topic.id],
            "subtopic_ids": [test_model_subtopic.id],
            "concept_ids": [test_model_concept.id],
            "answer_choices": answer_choices,
        }
        response = logged_in_client.post("/questions/with-answers/", json=question_data)
        questions.append(response.json())
    return questions


@pytest.fixture(scope="function")
def test_user_responses(logged_in_client, test_users, test_questions_with_answers):
    """Create test user responses via API."""
    user_responses = []
    for user in test_users:
        for question in test_questions_with_answers:
            correct_answer = next(
                (
                    answer
                    for answer in question["answer_choices"]
                    if answer["is_correct"]
                ),
                None,
            )
            response_data = {
                "user_id": user["id"],
                "question_id": question["id"],
                "answer_choice_id": correct_answer["id"],
            }
            response = logged_in_client.post("/user-responses/", json=response_data)
            logger.debug("Response in create_user_responses %s", response.json())
            user_responses.append(response.json())
    return user_responses


@pytest.fixture(scope="function")
def setup_test_data(test_questions_with_answers, test_user_responses):
    """Setup fixture that ensures all test data is created and can be used as a single dependency."""
    pass


@pytest.fixture(scope="function")
def test_user_data(test_schema_user):
    """Convert user schema to dictionary format with hashed password."""
    user_data = test_schema_user.model_dump()
    logger.debug("test_user_data: %s", user_data)
    user_data["hashed_password"] = get_password_hash(user_data["password"])
    return user_data


@pytest.fixture(scope="function")
def test_group_data(test_schema_group):
    """Convert group schema to dictionary format."""
    logger.debug("test_group_data: %s", test_schema_group.model_dump())
    return test_schema_group.model_dump()


@pytest.fixture(scope="function")
def test_role_data(test_schema_role):
    """Convert role schema to dictionary format."""
    logger.debug("test_role_data: %s", test_schema_role.model_dump())
    return test_schema_role.model_dump()


@pytest.fixture(scope="function")
def test_question_set_data(test_schema_question_set):
    """Convert question set schema to dictionary format."""
    logger.debug("test_question_set_data: %s", test_schema_question_set.model_dump())
    return test_schema_question_set.model_dump()