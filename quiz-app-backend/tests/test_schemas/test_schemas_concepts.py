# filename: tests/test_schemas/test_schemas_concepts.py

import pytest
from pydantic import ValidationError
from app.schemas.concepts import ConceptBaseSchema, ConceptCreateSchema, ConceptUpdateSchema, ConceptSchema

def test_concept_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        ConceptBaseSchema(name="")
    assert "Concept name cannot be empty or whitespace" in str(exc_info.value)
    
    with pytest.raises(ValidationError) as exc_info:
        ConceptBaseSchema(name="a" * 101)
    assert "String should have at most 100 characters" in str(exc_info.value)
    
    valid_concept = ConceptBaseSchema(name="Valid Concept")
    assert valid_concept.name == "Valid Concept"

def test_concept_create_schema():
    with pytest.raises(ValidationError) as exc_info:
        ConceptCreateSchema(name="Valid Concept", subtopic_ids=[])
    assert "List should have at least 1 item after validation" in str(exc_info.value)
    
    with pytest.raises(ValidationError) as exc_info:
        ConceptCreateSchema(name="Valid Concept", subtopic_ids=[1, 1])
    assert "Subtopic IDs must be unique" in str(exc_info.value)
    
    valid_concept = ConceptCreateSchema(name="Valid Concept", subtopic_ids=[1, 2, 3])
    assert valid_concept.name == "Valid Concept"
    assert valid_concept.subtopic_ids == [1, 2, 3]

def test_concept_update_schema():
    valid_update = ConceptUpdateSchema(name="Updated Concept", subtopic_ids=[1, 2, 3])
    assert valid_update.name == "Updated Concept"
    assert valid_update.subtopic_ids == [1, 2, 3]

    partial_update = ConceptUpdateSchema(name="Partial Update")
    assert partial_update.name == "Partial Update"
    assert partial_update.subtopic_ids is None

    with pytest.raises(ValidationError) as exc_info:
        ConceptUpdateSchema(name="", subtopic_ids=[1, 1])
    assert "Concept name cannot be empty or whitespace" in str(exc_info.value)
    assert "Subtopic IDs must be unique" in str(exc_info.value)

def test_concept_schema():
    concept = ConceptSchema(id=1, name="Test Concept", subtopics=[{"id": 1, "name": "Subtopic 1"}, {"id": 2, "name": "Subtopic 2"}], questions=[{"id": 3, "name": "Question 1"}, {"id": 4, "name": "Question 2"}])
    assert concept.id == 1
    assert concept.name == "Test Concept"
    assert len(concept.subtopics) == 2
    assert len(concept.questions) == 2
    assert concept.subtopics[0]["id"] == 1
    assert concept.subtopics[1]["id"] == 2
    assert concept.questions[0]["id"] == 3
    assert concept.questions[1]["id"] == 4
    assert concept.subtopics[0]["name"] == "Subtopic 1"
    assert concept.subtopics[1]["name"] == "Subtopic 2"
    assert concept.questions[0]["name"] == "Question 1"
    assert concept.questions[1]["name"] == "Question 2"

def test_concept_schema_from_attributes(test_concept):
    schema = ConceptSchema.model_validate(test_concept)
    assert schema.id == test_concept.id
    assert schema.name == test_concept.name
    assert isinstance(schema.subtopics, list)
    assert isinstance(schema.questions, list)
    for subtopic in schema.subtopics:
        assert "id" in subtopic
        assert "name" in subtopic
    for question in schema.questions:
        assert "id" in question
        assert "name" in question
