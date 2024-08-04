# filename: tests/test_schemas_topics.py

import pytest
from pydantic import ValidationError
from app.schemas.topics import TopicBaseSchema, TopicCreateSchema, TopicUpdateSchema, TopicSchema

def test_topic_base_schema_valid():
    data = {
        "name": "Algebra"
    }
    schema = TopicBaseSchema(**data)
    assert schema.name == "Algebra"

def test_topic_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        TopicBaseSchema(name="")
    assert "Topic name cannot be empty or whitespace" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        TopicBaseSchema(name="a" * 101)
    assert "String should have at most 100 characters" in str(exc_info.value)

def test_topic_create_schema():
    data = {
        "name": "Calculus",
        "subject_ids": [1, 2],
        "subtopic_ids": [3, 4, 5]
    }
    schema = TopicCreateSchema(**data)
    assert schema.name == "Calculus"
    assert schema.subject_ids == [1, 2]
    assert schema.subtopic_ids == [3, 4, 5]

def test_topic_create_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        TopicCreateSchema(name="Calculus", subject_ids=[])
    assert "List should have at least 1 item after validation" in str(exc_info.value)

def test_topic_update_schema():
    data = {
        "name": "Updated Calculus",
        "subject_ids": [2, 3],
        "subtopic_ids": [4, 5, 6]
    }
    schema = TopicUpdateSchema(**data)
    assert schema.name == "Updated Calculus"
    assert schema.subject_ids == [2, 3]
    assert schema.subtopic_ids == [4, 5, 6]

    # Test partial update
    partial_data = {"name": "Partially Updated Topic"}
    partial_schema = TopicUpdateSchema(**partial_data)
    assert partial_schema.name == "Partially Updated Topic"
    assert partial_schema.subject_ids is None
    assert partial_schema.subtopic_ids is None

def test_topic_schema():
    data = {
        "id": 1,
        "name": "Complete Topic",
        "subjects": [{"id": 1, "name": "Subject 1"}, {"id": 2, "name": "Subject 2"}],
        "subtopics": [{"id": 3, "name": "Subtopic 1"}, {"id": 4, "name": "Subtopic 2"}, {"id": 5, "name": "Subtopic 3"}],
        "questions": [{"id": 6, "name": "Question 1"}, {"id": 7, "name": "Question 2"}]
    }
    schema = TopicSchema(**data)
    assert schema.id == 1
    assert schema.name == "Complete Topic"
    assert len(schema.subjects) == 2
    assert len(schema.subtopics) == 3
    assert len(schema.questions) == 2
    assert schema.subjects[0]["id"] == 1
    assert schema.subjects[1]["id"] == 2
    assert schema.subtopics[0]["id"] == 3
    assert schema.subtopics[1]["id"] == 4
    assert schema.subtopics[2]["id"] == 5
    assert schema.questions[0]["id"] == 6
    assert schema.questions[1]["id"] == 7

def test_topic_schema_from_attributes(db_session, test_topic):
    schema = TopicSchema.model_validate(test_topic)
    assert schema.id == test_topic.id
    assert schema.name == test_topic.name
    assert isinstance(schema.subjects, list)
    assert isinstance(schema.subtopics, list)
    assert isinstance(schema.questions, list)
    for subject in schema.subjects:
        assert "id" in subject
        assert "name" in subject
    for subtopic in schema.subtopics:
        assert "id" in subtopic
        assert "name" in subtopic
    for question in schema.questions:
        assert "id" in question
        assert "name" in question
