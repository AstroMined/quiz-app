# filename: backend/tests/test_schemas_question_tags.py

import pytest
from pydantic import ValidationError

from backend.app.schemas.question_tags import (
    QuestionTagBaseSchema,
    QuestionTagCreateSchema,
    QuestionTagSchema,
    QuestionTagUpdateSchema,
)


def test_question_tag_base_schema_valid():
    data = {"tag": "mathematics"}
    schema = QuestionTagBaseSchema(**data)
    assert schema.tag == "mathematics"


def test_question_tag_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        QuestionTagBaseSchema(tag="")
    assert "String should have at least 1 character" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        QuestionTagBaseSchema(tag="a" * 51)
    assert "String should have at most 50 characters" in str(exc_info.value)


def test_question_tag_base_schema_lowercase():
    data = {"tag": "UPPERCASE"}
    schema = QuestionTagBaseSchema(**data)
    assert schema.tag == "uppercase"


def test_question_tag_create_schema():
    data = {"tag": "physics"}
    schema = QuestionTagCreateSchema(**data)
    assert schema.tag == "physics"


def test_question_tag_update_schema():
    data = {"tag": "updated_tag"}
    schema = QuestionTagUpdateSchema(**data)
    assert schema.tag == "updated_tag"

    # Test partial update (although in this case, there's only one field)
    partial_data = {}
    partial_schema = QuestionTagUpdateSchema(**partial_data)
    assert partial_schema.tag is None


def test_question_tag_schema():
    data = {"id": 1, "tag": "biology"}
    schema = QuestionTagSchema(**data)
    assert schema.id == 1
    assert schema.tag == "biology"


def test_question_tag_schema_from_attributes(db_session, test_model_tag):
    schema = QuestionTagSchema.model_validate(test_model_tag)
    assert schema.id == test_model_tag.id
    assert schema.tag == test_model_tag.tag.lower()
