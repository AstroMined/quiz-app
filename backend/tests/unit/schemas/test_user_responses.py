# filename: backend/tests/test_schemas_user_responses.py

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from backend.app.schemas.user_responses import (
    UserResponseBaseSchema,
    UserResponseCreateSchema,
    UserResponseSchema,
    UserResponseUpdateSchema,
)


def test_user_response_base_schema_valid():
    data = {
        "user_id": 1,
        "question_id": 1,
        "answer_choice_id": 1,
        "is_correct": True,
        "response_time": 30,
    }
    schema = UserResponseBaseSchema(**data)
    assert schema.user_id == 1
    assert schema.question_id == 1
    assert schema.answer_choice_id == 1
    assert schema.is_correct is True
    assert schema.response_time == 30


def test_user_response_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        UserResponseBaseSchema(
            user_id=0, question_id=1, answer_choice_id=1, is_correct=True
        )
    assert "Input should be greater than 0" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        UserResponseBaseSchema(
            user_id=1,
            question_id=1,
            answer_choice_id=1,
            is_correct=True,
            response_time=-1,
        )
    assert "Input should be greater than or equal to 0" in str(exc_info.value)


def test_user_response_create_schema():
    data = {
        "user_id": 1,
        "question_id": 1,
        "answer_choice_id": 1,
        "is_correct": True,
        "response_time": 30,
        "timestamp": datetime.now(timezone.utc),
    }
    schema = UserResponseCreateSchema(**data)
    assert schema.user_id == 1
    assert schema.question_id == 1
    assert schema.answer_choice_id == 1
    assert schema.is_correct is True
    assert schema.response_time == 30
    assert isinstance(schema.timestamp, datetime)


def test_user_response_update_schema():
    data = {"is_correct": False, "response_time": 45}
    schema = UserResponseUpdateSchema(**data)
    assert schema.is_correct is False
    assert schema.response_time == 45

    # Test partial update
    partial_data = {"is_correct": True}
    partial_schema = UserResponseUpdateSchema(**partial_data)
    assert partial_schema.is_correct is True
    assert partial_schema.response_time is None


def test_user_response_schema():
    data = {
        "id": 1,
        "user_id": 1,
        "question_id": 1,
        "answer_choice_id": 1,
        "is_correct": True,
        "response_time": 30,
        "timestamp": datetime.now(timezone.utc),
    }
    schema = UserResponseSchema(**data)
    assert schema.id == 1
    assert schema.user_id == 1
    assert schema.question_id == 1
    assert schema.answer_choice_id == 1
    assert schema.is_correct is True
    assert schema.response_time == 30
    assert isinstance(schema.timestamp, datetime)


