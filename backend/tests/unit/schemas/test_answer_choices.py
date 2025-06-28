# filename: backend/tests/test_schemas_answer_choices.py

import pytest
from pydantic import ValidationError

from backend.app.schemas.answer_choices import (
    AnswerChoiceBaseSchema,
    AnswerChoiceCreateSchema,
    AnswerChoiceSchema,
    AnswerChoiceUpdateSchema,
)


def test_answer_choice_base_schema_valid():
    data = {
        "text": "This is a valid answer choice",
        "is_correct": True,
        "explanation": "This is a valid explanation",
    }
    schema = AnswerChoiceBaseSchema(**data)
    assert schema.text == "This is a valid answer choice"
    assert schema.is_correct is True
    assert schema.explanation == "This is a valid explanation"


def test_answer_choice_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        AnswerChoiceBaseSchema(text="", is_correct=True)
    assert "String should have at least 1 character" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        AnswerChoiceBaseSchema(text="a" * 10001, is_correct=True)
    assert "String should have at most 10000 characters" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        AnswerChoiceBaseSchema(text="Valid text", is_correct="not a boolean")
    assert "Input should be a valid boolean" in str(exc_info.value)


def test_answer_choice_create_schema():
    data = {
        "text": "This is a new answer choice",
        "is_correct": False,
        "explanation": "This is an explanation for the new answer choice",
    }
    schema = AnswerChoiceCreateSchema(**data)
    assert schema.text == "This is a new answer choice"
    assert schema.is_correct is False
    assert schema.explanation == "This is an explanation for the new answer choice"


def test_answer_choice_update_schema():
    data = {"text": "Updated answer choice", "is_correct": True}
    schema = AnswerChoiceUpdateSchema(**data)
    assert schema.text == "Updated answer choice"
    assert schema.is_correct is True
    assert schema.explanation is None

    # Test partial update
    partial_data = {"text": "Partially updated answer"}
    partial_schema = AnswerChoiceUpdateSchema(**partial_data)
    assert partial_schema.text == "Partially updated answer"
    assert partial_schema.is_correct is None
    assert partial_schema.explanation is None


def test_answer_choice_schema():
    data = {
        "id": 1,
        "text": "This is a complete answer choice",
        "is_correct": True,
        "explanation": "This is a complete explanation",
    }
    schema = AnswerChoiceSchema(**data)
    assert schema.id == 1
    assert schema.text == "This is a complete answer choice"
    assert schema.is_correct is True
    assert schema.explanation == "This is a complete explanation"


def test_answer_choice_schema_from_orm(test_model_answer_choices):
    orm_object = test_model_answer_choices[0]
    schema = AnswerChoiceSchema.model_validate(orm_object)
    assert schema.id == orm_object.id
    assert schema.text == orm_object.text
    assert schema.is_correct == orm_object.is_correct
    assert schema.explanation == orm_object.explanation
