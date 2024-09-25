# filename: backend/tests/test_schemas_subtopics.py

import pytest
from pydantic import ValidationError

from backend.app.schemas.subtopics import (
    SubtopicBaseSchema,
    SubtopicCreateSchema,
    SubtopicSchema,
    SubtopicUpdateSchema,
)


def test_subtopic_base_schema_valid():
    data = {"name": "Linear Equations"}
    schema = SubtopicBaseSchema(**data)
    assert schema.name == "Linear Equations"


def test_subtopic_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        SubtopicBaseSchema(name="")
    assert "Subtopic name cannot be empty or whitespace" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        SubtopicBaseSchema(name="a" * 101)
    assert "String should have at most 100 characters" in str(exc_info.value)


def test_subtopic_create_schema():
    data = {
        "name": "Quadratic Equations",
        "topic_ids": [1, 2],
        "concept_ids": [3, 4, 5],
    }
    schema = SubtopicCreateSchema(**data)
    assert schema.name == "Quadratic Equations"
    assert schema.topic_ids == [1, 2]
    assert schema.concept_ids == [3, 4, 5]


def test_subtopic_create_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        SubtopicCreateSchema(name="Quadratic Equations", topic_ids=[])
    assert "List should have at least 1 item after validation" in str(exc_info.value)


def test_subtopic_update_schema():
    data = {
        "name": "Updated Quadratic Equations",
        "topic_ids": [2, 3],
        "concept_ids": [4, 5, 6],
    }
    schema = SubtopicUpdateSchema(**data)
    assert schema.name == "Updated Quadratic Equations"
    assert schema.topic_ids == [2, 3]
    assert schema.concept_ids == [4, 5, 6]

    # Test partial update
    partial_data = {"name": "Partially Updated Subtopic"}
    partial_schema = SubtopicUpdateSchema(**partial_data)
    assert partial_schema.name == "Partially Updated Subtopic"
    assert partial_schema.topic_ids is None
    assert partial_schema.concept_ids is None


def test_subtopic_schema():
    data = {
        "id": 1,
        "name": "Complete Subtopic",
        "topics": [{"id": 1, "name": "Topic 1"}, {"id": 2, "name": "Topic 2"}],
        "concepts": [
            {"id": 3, "name": "Concept 1"},
            {"id": 4, "name": "Concept 2"},
            {"id": 5, "name": "Concept 3"},
        ],
        "questions": [{"id": 6, "name": "Question 1"}, {"id": 7, "name": "Question 2"}],
    }
    schema = SubtopicSchema(**data)
    assert schema.id == 1
    assert schema.name == "Complete Subtopic"
    assert len(schema.topics) == 2
    assert len(schema.concepts) == 3
    assert len(schema.questions) == 2
    assert schema.topics[0]["id"] == 1
    assert schema.topics[1]["id"] == 2
    assert schema.concepts[0]["id"] == 3
    assert schema.concepts[1]["id"] == 4
    assert schema.concepts[2]["id"] == 5
    assert schema.questions[0]["id"] == 6
    assert schema.questions[1]["id"] == 7


def test_subtopic_schema_from_attributes(test_model_subtopic):
    schema = SubtopicSchema.model_validate(test_model_subtopic)
    assert schema.id == test_model_subtopic.id
    assert schema.name == test_model_subtopic.name
    assert isinstance(schema.topics, list)
    assert isinstance(schema.concepts, list)
    assert isinstance(schema.questions, list)
    for topic in schema.topics:
        assert "id" in topic
        assert "name" in topic
    for concept in schema.concepts:
        assert "id" in concept
        assert "name" in concept
    for question in schema.questions:
        assert "id" in question
        assert "name" in question
