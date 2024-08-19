# filename: backend/tests/test_schemas/test_schemas_subjects.py

import pytest
from pydantic import ValidationError

from backend.app.schemas.subjects import (SubjectBaseSchema,
                                          SubjectCreateSchema, SubjectSchema,
                                          SubjectUpdateSchema)


def test_subject_base_schema_valid():
    data = {
        "name": "Mathematics"
    }
    schema = SubjectBaseSchema(**data)
    assert schema.name == "Mathematics"

def test_subject_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        SubjectBaseSchema(name="")
    assert "Subject name cannot be empty or whitespace" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        SubjectBaseSchema(name="a" * 101)
    assert "String should have at most 100 characters" in str(exc_info.value)

def test_subject_create_schema():
    data = {
        "name": "Physics",
        "discipline_ids": [1, 2],
        "topic_ids": [3, 4, 5]
    }
    schema = SubjectCreateSchema(**data)
    assert schema.name == "Physics"
    assert schema.discipline_ids == [1, 2]
    assert schema.topic_ids == [3, 4, 5]

def test_subject_create_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        SubjectCreateSchema(name="Physics", discipline_ids=[])
    assert "List should have at least 1 item after validation" in str(exc_info.value)

def test_subject_update_schema():
    data = {
        "name": "Updated Physics",
        "discipline_ids": [2, 3],
        "topic_ids": [4, 5, 6]
    }
    schema = SubjectUpdateSchema(**data)
    assert schema.name == "Updated Physics"
    assert schema.discipline_ids == [2, 3]
    assert schema.topic_ids == [4, 5, 6]

    # Test partial update
    partial_data = {"name": "Partially Updated Subject"}
    partial_schema = SubjectUpdateSchema(**partial_data)
    assert partial_schema.name == "Partially Updated Subject"
    assert partial_schema.discipline_ids is None
    assert partial_schema.topic_ids is None

def test_subject_schema():
    data = {
        "id": 1,
        "name": "Complete Subject",
        "disciplines": [{"id": 1, "name": "Discipline 1"}, {"id": 2, "name": "Discipline 2"}],
        "topics": [{"id": 3, "name": "Topic 1"}, {"id": 4, "name": "Topic 2"}, {"id": 5, "name": "Topic 3"}],
        "questions": [{"id": 6, "name": "Question 1"}, {"id": 7, "name": "Question 2"}]
    }
    schema = SubjectSchema(**data)
    assert schema.id == 1
    assert schema.name == "Complete Subject"
    assert len(schema.disciplines) == 2
    assert len(schema.topics) == 3
    assert len(schema.questions) == 2
    assert schema.disciplines[0]["id"] == 1
    assert schema.disciplines[1]["id"] == 2
    assert schema.topics[0]["id"] == 3
    assert schema.topics[1]["id"] == 4
    assert schema.topics[2]["id"] == 5
    assert schema.questions[0]["id"] == 6
    assert schema.questions[1]["id"] == 7

def test_subject_schema_from_attributes(db_session, test_model_subject):
    schema = SubjectSchema.model_validate(test_model_subject)
    assert schema.id == test_model_subject.id
    assert schema.name == test_model_subject.name
    assert isinstance(schema.disciplines, list)
    assert isinstance(schema.topics, list)
    assert isinstance(schema.questions, list)
    for discipline in schema.disciplines:
        assert "id" in discipline
        assert "name" in discipline
    for topic in schema.topics:
        assert "id" in topic
        assert "name" in topic
    for question in schema.questions:
        assert "id" in question
        assert "name" in question
