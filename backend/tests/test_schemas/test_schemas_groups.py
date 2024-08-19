# filename: backend/tests/test_schemas/test_schemas_groups.py

import pytest
from pydantic import ValidationError

from backend.app.schemas.groups import (GroupBaseSchema, GroupCreateSchema,
                                        GroupSchema, GroupUpdateSchema)


def test_group_base_schema_valid():
    data = {
        "name": "Test Group",
        "description": "This is a test group"
    }
    schema = GroupBaseSchema(**data)
    assert schema.name == "Test Group"
    assert schema.description == "This is a test group"

def test_group_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        GroupBaseSchema(name="", description="Invalid group")
    assert "String should have at least 1 character" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        GroupBaseSchema(name="a" * 101, description="Invalid group")
    assert "String should have at most 100 characters" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        GroupBaseSchema(name="Invalid@Group", description="Invalid group")
    assert "Group name can only contain alphanumeric characters, hyphens, underscores, and spaces" in str(exc_info.value)

def test_group_create_schema(test_model_user):
    data = {
        "name": "New Group",
        "description": "This is a new group",
        "creator_id": test_model_user.id
    }
    schema = GroupCreateSchema(**data)
    assert schema.name == "New Group"
    assert schema.description == "This is a new group"
    assert schema.creator_id == test_model_user.id

def test_group_update_schema():
    data = {
        "name": "Updated Group",
        "description": "This group has been updated"
    }
    schema = GroupUpdateSchema(**data)
    assert schema.name == "Updated Group"
    assert schema.description == "This group has been updated"

    # Test partial update
    partial_data = {"name": "Partially Updated Group"}
    partial_schema = GroupUpdateSchema(**partial_data)
    assert partial_schema.name == "Partially Updated Group"
    assert partial_schema.description is None

def test_group_schema(test_model_user):
    data = {
        "id": 1,
        "name": "Complete Group",
        "description": "This is a complete group",
        "creator_id": test_model_user.id,
        "users": [{"id": test_model_user.id, "name": "Test User"}],
        "question_sets": [{"id": 1, "name": "Question Set 1"}, {"id": 2, "name": "Question Set 2"}, {"id": 3, "name": "Question Set 3"}]
    }
    schema = GroupSchema(**data)
    assert schema.id == 1
    assert schema.name == "Complete Group"
    assert schema.description == "This is a complete group"
    assert schema.creator_id == test_model_user.id
    assert len(schema.users) == 1
    assert schema.users[0]["id"] == test_model_user.id
    assert len(schema.question_sets) == 3
    assert [qs["id"] for qs in schema.question_sets] == [1, 2, 3]

def test_group_schema_from_attributes(test_model_group):
    schema = GroupSchema.model_validate(test_model_group)
    assert schema.id == test_model_group.id
    assert schema.name == test_model_group.name
    assert schema.description == test_model_group.description
    assert schema.creator_id == test_model_group.creator_id
    assert isinstance(schema.users, list)
    assert isinstance(schema.question_sets, list)
    for user in schema.users:
        assert "id" in user
        assert "name" in user
    for question_set in schema.question_sets:
        assert "id" in question_set
        assert "name" in question_set
