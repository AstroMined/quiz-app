# filename: backend/tests/test_schemas_filters.py

import pytest
from pydantic import ValidationError

from backend.app.schemas.filters import FilterParamsSchema
from backend.app.schemas.questions import DifficultyLevel


def test_filter_params_schema_valid():
    data = {
        "subject": "Mathematics",
        "topic": "Algebra",
        "subtopic": "Linear Equations",
        "difficulty": DifficultyLevel.MEDIUM,
        "question_tags": ["math", "algebra"]
    }
    schema = FilterParamsSchema(**data)
    assert schema.subject == "Mathematics"
    assert schema.topic == "Algebra"
    assert schema.subtopic == "Linear Equations"
    assert schema.difficulty == DifficultyLevel.MEDIUM
    assert schema.question_tags == ["math", "algebra"]

def test_filter_params_schema_optional_fields():
    data = {
        "subject": "Physics"
    }
    schema = FilterParamsSchema(**data)
    assert schema.subject == "Physics"
    assert schema.topic is None
    assert schema.subtopic is None
    assert schema.difficulty is None
    assert schema.question_tags is None

def test_filter_params_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        FilterParamsSchema(subject="a" * 101)
    assert "String should have at most 100 characters" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        FilterParamsSchema(difficulty="Invalid")
    assert "Input should be 'Beginner', 'Easy', 'Medium', 'Hard' or 'Expert'" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        FilterParamsSchema(question_tags=["tag1", "tag2"] * 6)
    assert "List should have at most 10 items after validation" in str(exc_info.value)

def test_filter_params_schema_question_tags_lowercase():
    data = {
        "question_tags": ["MATH", "Algebra", "LINEAR"]
    }
    schema = FilterParamsSchema(**data)
    assert schema.question_tags == ["math", "algebra", "linear"]

def test_filter_params_schema_extra_fields():
    with pytest.raises(ValidationError) as exc_info:
        FilterParamsSchema(subject="Math", extra_field="Invalid")
    assert "Extra inputs are not permitted" in str(exc_info.value)
