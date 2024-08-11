# filename: tests/test_schemas_roles.py

import pytest
from pydantic import ValidationError
from app.schemas.roles import RoleBaseSchema, RoleCreateSchema, RoleUpdateSchema, RoleSchema

def test_role_base_schema_valid():
    data = {
        "name": "admin",
        "description": "Administrator role",
        "default": False
    }
    schema = RoleBaseSchema(**data)
    assert schema.name == "admin"
    assert schema.description == "Administrator role"
    assert schema.default is False

def test_role_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        RoleBaseSchema(name="", description="Invalid role", default=False)
    assert "String should have at least 1 character" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        RoleBaseSchema(name="a" * 51, description="Invalid role", default=False)
    assert "String should have at most 50 characters" in str(exc_info.value)

def test_role_create_schema():
    data = {
        "name": "moderator",
        "description": "Moderator role",
        "default": False,
        "permissions": ["read_post", "edit_post", "delete_post"]
    }
    schema = RoleCreateSchema(**data)
    assert schema.name == "moderator"
    assert schema.description == "Moderator role"
    assert schema.default is False
    assert set(schema.permissions) == set(["read_post", "edit_post", "delete_post"])

def test_role_create_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        RoleCreateSchema(name="invalid", description="Invalid role", default=False, permissions=[])
    assert "List should have at least 1 item after validation" in str(exc_info.value)

def test_role_update_schema():
    data = {
        "name": "editor",
        "description": "Updated editor role",
        "permissions": ["read_post", "edit_post"]
    }
    schema = RoleUpdateSchema(**data)
    assert schema.name == "editor"
    assert schema.description == "Updated editor role"
    assert set(schema.permissions) == set(["read_post", "edit_post"])  # Use set comparison

    # Test partial update
    partial_data = {"description": "Partially updated description"}
    partial_schema = RoleUpdateSchema(**partial_data)
    assert partial_schema.name is None
    assert partial_schema.description == "Partially updated description"
    assert partial_schema.permissions is None

def test_role_schema():
    data = {
        "id": 1,
        "name": "user",
        "description": "Regular user role",
        "default": True,
        "permissions": ["read_post", "create_post"]
    }
    schema = RoleSchema(**data)
    assert schema.id == 1
    assert schema.name == "user"
    assert schema.description == "Regular user role"
    assert schema.default is True
    assert set(schema.permissions) == set(["read_post", "create_post"])  # Use set comparison

def test_role_schema_from_attributes(test_model_role):
    schema = RoleSchema.model_validate(test_model_role)
    assert schema.id == test_model_role.id
    assert schema.name == test_model_role.name
    assert schema.description == test_model_role.description
    assert schema.default == test_model_role.default
    assert set(schema.permissions) == set(permission.name for permission in test_model_role.permissions)

# Add a new test for duplicate permissions
def test_role_schema_duplicate_permissions():
    data = {
        "id": 1,
        "name": "user",
        "description": "Regular user role",
        "default": True,
        "permissions": ["read_post", "create_post", "read_post"]
    }
    schema = RoleSchema(**data)
    assert set(schema.permissions) == set(["read_post", "create_post"])  # Duplicates should be removed
