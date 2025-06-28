# filename: backend/tests/test_schemas/test_schemas_domains.py

import pytest
from pydantic import ValidationError

from backend.app.schemas.domains import (
    DomainBaseSchema,
    DomainCreateSchema,
    DomainSchema,
    DomainUpdateSchema,
)


def test_domain_base_schema_valid():
    data = {"name": "Science and Technology"}
    schema = DomainBaseSchema(**data)
    assert schema.name == "Science and Technology"


def test_domain_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        DomainBaseSchema(name="")
    assert "Domain name cannot be empty or whitespace" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        DomainBaseSchema(name="a" * 101)
    assert "String should have at most 100 characters" in str(exc_info.value)


def test_domain_create_schema():
    data = {"name": "Arts and Humanities", "discipline_ids": [1, 2, 3]}
    schema = DomainCreateSchema(**data)
    assert schema.name == "Arts and Humanities"
    assert schema.discipline_ids == [1, 2, 3]


def test_domain_create_schema_optional_disciplines():
    data = {"name": "New Domain"}
    schema = DomainCreateSchema(**data)
    assert schema.name == "New Domain"
    assert schema.discipline_ids is None


def test_domain_update_schema():
    data = {"name": "Updated Arts and Humanities", "discipline_ids": [2, 3, 4]}
    schema = DomainUpdateSchema(**data)
    assert schema.name == "Updated Arts and Humanities"
    assert schema.discipline_ids == [2, 3, 4]

    # Test partial update
    partial_data = {"name": "Partially Updated Domain"}
    partial_schema = DomainUpdateSchema(**partial_data)
    assert partial_schema.name == "Partially Updated Domain"
    assert partial_schema.discipline_ids is None


def test_domain_schema():
    data = {
        "id": 1,
        "name": "Complete Domain",
        "disciplines": [
            {"id": 1, "name": "Discipline 1"},
            {"id": 2, "name": "Discipline 2"},
            {"id": 3, "name": "Discipline 3"},
        ],
    }
    schema = DomainSchema(**data)
    assert schema.id == 1
    assert schema.name == "Complete Domain"
    assert len(schema.disciplines) == 3
    assert schema.disciplines[0]["id"] == 1
    assert schema.disciplines[1]["id"] == 2
    assert schema.disciplines[2]["id"] == 3


