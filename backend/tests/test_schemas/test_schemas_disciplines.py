# filename: backend/tests/test_schemas/test_schemas_disciplines.py

import pytest
from pydantic import ValidationError

from backend.app.schemas.disciplines import (DisciplineBaseSchema,
                                             DisciplineCreateSchema,
                                             DisciplineSchema,
                                             DisciplineUpdateSchema)


def test_discipline_base_schema_valid():
    data = {
        "name": "Natural Sciences"
    }
    schema = DisciplineBaseSchema(**data)
    assert schema.name == "Natural Sciences"

def test_discipline_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        DisciplineBaseSchema(name="")
    assert "Discipline name cannot be empty or whitespace" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        DisciplineBaseSchema(name="a" * 101)
    assert "String should have at most 100 characters" in str(exc_info.value)

def test_discipline_create_schema():
    data = {
        "name": "Social Sciences",
        "domain_ids": [1, 2],
        "subject_ids": [3, 4, 5]
    }
    schema = DisciplineCreateSchema(**data)
    assert schema.name == "Social Sciences"
    assert schema.domain_ids == [1, 2]
    assert schema.subject_ids == [3, 4, 5]

def test_discipline_create_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        DisciplineCreateSchema(name="Social Sciences", domain_ids=[])
    assert "List should have at least 1 item after validation" in str(exc_info.value)

def test_discipline_update_schema():
    data = {
        "name": "Updated Social Sciences",
        "domain_ids": [2, 3],
        "subject_ids": [4, 5, 6]
    }
    schema = DisciplineUpdateSchema(**data)
    assert schema.name == "Updated Social Sciences"
    assert schema.domain_ids == [2, 3]
    assert schema.subject_ids == [4, 5, 6]

    # Test partial update
    partial_data = {"name": "Partially Updated Discipline"}
    partial_schema = DisciplineUpdateSchema(**partial_data)
    assert partial_schema.name == "Partially Updated Discipline"
    assert partial_schema.domain_ids is None
    assert partial_schema.subject_ids is None

def test_discipline_schema():
    data = {
        "id": 1,
        "name": "Complete Discipline",
        "domains": [{"id": 1, "name": "Domain 1"}, {"id": 2, "name": "Domain 2"}],
        "subjects": [{"id": 3, "name": "Subject 1"}, {"id": 4, "name": "Subject 2"}, {"id": 5, "name": "Subject 3"}]
    }
    schema = DisciplineSchema(**data)
    assert schema.id == 1
    assert schema.name == "Complete Discipline"
    assert len(schema.domains) == 2
    assert len(schema.subjects) == 3
    assert schema.domains[0]["id"] == 1
    assert schema.domains[1]["id"] == 2
    assert schema.subjects[0]["id"] == 3
    assert schema.subjects[1]["id"] == 4
    assert schema.subjects[2]["id"] == 5

def test_discipline_schema_from_attributes(test_model_discipline):
    schema = DisciplineSchema.model_validate(test_model_discipline)
    assert schema.id == test_model_discipline.id
    assert schema.name == test_model_discipline.name
    assert isinstance(schema.domains, list)
    assert isinstance(schema.subjects, list)
    for domain in schema.domains:
        assert "id" in domain
        assert "name" in domain
    for subject in schema.subjects:
        assert "id" in subject
        assert "name" in subject
