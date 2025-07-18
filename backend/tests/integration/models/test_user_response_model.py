# filename: backend/tests/models/test_user_response_model.py

from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from backend.app.models.user_responses import UserResponseModel
from backend.app.schemas.user_responses import UserResponseSchema


def test_user_response_creation(
    db_session, test_model_user, test_model_questions, test_model_answer_choices
):
    user_response = UserResponseModel(
        user_id=test_model_user.id,
        question_id=test_model_questions[0].id,
        answer_choice_id=test_model_answer_choices[0].id,
        is_correct=True,
    )
    db_session.add(user_response)
    db_session.commit()

    assert user_response.id is not None
    assert user_response.user_id == test_model_user.id
    assert user_response.question_id == test_model_questions[0].id
    assert user_response.answer_choice_id == test_model_answer_choices[0].id
    assert user_response.is_correct is True
    assert user_response.timestamp is not None


def test_user_response_relationships(
    db_session, test_model_user, test_model_questions, test_model_answer_choices
):
    user_response = UserResponseModel(
        user_id=test_model_user.id,
        question_id=test_model_questions[0].id,
        answer_choice_id=test_model_answer_choices[0].id,
        is_correct=True,
    )
    db_session.add(user_response)
    db_session.commit()

    assert user_response.user == test_model_user
    assert user_response.question == test_model_questions[0]
    assert user_response.answer_choice == test_model_answer_choices[0]
    assert user_response in test_model_user.responses
    assert user_response in test_model_questions[0].user_responses
    assert user_response in test_model_answer_choices[0].user_responses


def test_user_response_required_fields(
    db_session, test_model_user, test_model_questions, test_model_answer_choices
):
    # Store IDs to avoid accessing potentially detached objects
    user_id = test_model_user.id
    question_id = test_model_questions[0].id
    answer_choice_id = test_model_answer_choices[0].id
    
    # Test missing user_id
    with pytest.raises(IntegrityError):
        user_response = UserResponseModel(
            question_id=question_id,
            answer_choice_id=answer_choice_id,
            is_correct=True,
        )
        db_session.add(user_response)
        db_session.commit()
    db_session.rollback()

    # Test missing question_id
    with pytest.raises(IntegrityError):
        user_response = UserResponseModel(
            user_id=user_id,
            answer_choice_id=answer_choice_id,
            is_correct=True,
        )
        db_session.add(user_response)
        db_session.commit()
    db_session.rollback()

    # Test missing answer_choice_id
    with pytest.raises(IntegrityError):
        user_response = UserResponseModel(
            user_id=user_id,
            question_id=question_id,
            is_correct=True,
        )
        db_session.add(user_response)
        db_session.commit()
    db_session.rollback()


def test_user_response_repr(
    db_session, test_model_user, test_model_questions, test_model_answer_choices
):
    user_response = UserResponseModel(
        user_id=test_model_user.id,
        question_id=test_model_questions[0].id,
        answer_choice_id=test_model_answer_choices[0].id,
        is_correct=True,
    )
    db_session.add(user_response)
    db_session.commit()

    expected_repr = f"<UserResponseModel(id={user_response.id}, user_id={test_model_user.id}, question_id={test_model_questions[0].id}, is_correct=True)>"
    assert repr(user_response) == expected_repr


def test_user_response_schema_from_attributes(
    db_session, test_model_user, test_model_questions, test_model_answer_choices
):
    """Test schema validation from model attributes - integration test."""
    user_response = UserResponseModel(
        user_id=test_model_user.id,
        question_id=test_model_questions[0].id,
        answer_choice_id=test_model_answer_choices[0].id,
        is_correct=True,
        response_time=30,
    )
    db_session.add(user_response)
    db_session.commit()
    db_session.refresh(user_response)

    schema = UserResponseSchema.model_validate(user_response)
    assert schema.id == user_response.id
    assert schema.user_id == test_model_user.id
    assert schema.question_id == test_model_questions[0].id
    assert schema.answer_choice_id == test_model_answer_choices[0].id
    assert schema.is_correct is True
    assert schema.response_time == 30
    assert isinstance(schema.timestamp, datetime)
