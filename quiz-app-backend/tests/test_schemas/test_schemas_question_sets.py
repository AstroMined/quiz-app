# filename: tests/test_schemas/test_schemas_question_sets.py

import pytest
from pydantic import ValidationError
from app.schemas.question_sets import QuestionSetBaseSchema, QuestionSetCreateSchema, QuestionSetUpdateSchema, QuestionSetSchema

def test_question_set_base_schema_valid():
    data = {
        "name": "Math Quiz Set",
        "description": "A set of math questions",
        "is_public": True
    }
    schema = QuestionSetBaseSchema(**data)
    assert schema.name == "Math Quiz Set"
    assert schema.description == "A set of math questions"
    assert schema.is_public is True

def test_question_set_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        QuestionSetBaseSchema(name="", description="Invalid set", is_public=True)
    assert "String should have at least 1 character" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        QuestionSetBaseSchema(name="a" * 201, description="Invalid set", is_public=True)
    assert "String should have at most 200 characters" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        QuestionSetBaseSchema(name="Invalid@Set", description="Invalid set", is_public=True)
    assert "Question set name can only contain alphanumeric characters, hyphens, underscores, and spaces" in str(exc_info.value)

def test_question_set_create_schema(test_user):
    data = {
        "name": "Science Quiz Set",
        "description": "A set of science questions",
        "is_public": False,
        "creator_id": test_user.id,
        "question_ids": [1, 2, 3],
        "group_ids": [1, 2]
    }
    schema = QuestionSetCreateSchema(**data)
    assert schema.name == "Science Quiz Set"
    assert schema.description == "A set of science questions"
    assert schema.is_public is False
    assert schema.creator_id == test_user.id
    assert schema.question_ids == [1, 2, 3]
    assert schema.group_ids == [1, 2]

def test_question_set_update_schema():
    data = {
        "name": "Updated Quiz Set",
        "description": "This set has been updated",
        "is_public": True,
        "question_ids": [4, 5, 6],
        "group_ids": [3, 4]
    }
    schema = QuestionSetUpdateSchema(**data)
    assert schema.name == "Updated Quiz Set"
    assert schema.description == "This set has been updated"
    assert schema.is_public is True
    assert schema.question_ids == [4, 5, 6]
    assert schema.group_ids == [3, 4]

    # Test partial update
    partial_data = {"name": "Partially Updated Set"}
    partial_schema = QuestionSetUpdateSchema(**partial_data)
    assert partial_schema.name == "Partially Updated Set"
    assert partial_schema.description is None
    assert partial_schema.is_public is None
    assert partial_schema.question_ids is None
    assert partial_schema.group_ids is None

def test_question_set_schema():
    data = {
        "id": 1,
        "name": "Complete Quiz Set",
        "description": "This is a complete question set",
        "is_public": True,
        "creator_id": 1,
        "questions": [{"id": 1, "name": "Question 1"}, {"id": 2, "name": "Question 2"}],
        "groups": [{"id": 1, "name": "Group 1"}, {"id": 2, "name": "Group 2"}]
    }
    schema = QuestionSetSchema(**data)
    assert schema.id == 1
    assert schema.name == "Complete Quiz Set"
    assert schema.description == "This is a complete question set"
    assert schema.is_public is True
    assert schema.creator_id == 1
    assert len(schema.questions) == 2
    assert len(schema.groups) == 2
    assert schema.questions[0]["id"] == 1
    assert schema.groups[0]["id"] == 1

def test_question_set_schema_from_attributes(test_question_set):
    schema = QuestionSetSchema.model_validate(test_question_set)
    assert schema.id == test_question_set.id
    assert schema.name == test_question_set.name
    assert schema.description == test_question_set.description
    assert schema.is_public == test_question_set.is_public
    assert schema.creator_id == test_question_set.creator_id
    assert isinstance(schema.questions, list)
    assert isinstance(schema.groups, list)
    for question in schema.questions:
        assert "id" in question
        assert "name" in question
    for group in schema.groups:
        assert "id" in group
        assert "name" in group
