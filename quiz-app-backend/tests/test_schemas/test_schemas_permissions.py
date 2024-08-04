# filename: tests/test_schemas_permissions.py

import pytest
from pydantic import ValidationError
from app.schemas.permissions import PermissionBaseSchema, PermissionCreateSchema, PermissionUpdateSchema, PermissionSchema

def test_permission_base_schema_valid():
    data = {
        "name": "create_user",
        "description": "Permission to create a new user"
    }
    schema = PermissionBaseSchema(**data)
    assert schema.name == "create_user"
    assert schema.description == "Permission to create a new user"

def test_permission_base_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        PermissionBaseSchema(name="", description="Invalid permission")
    assert "String should have at least 1 character" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        PermissionBaseSchema(name="a" * 101, description="Invalid permission")
    assert "String should have at most 100 characters" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        PermissionBaseSchema(name="invalid@permission", description="Invalid permission")
    assert "Permission name can only contain alphanumeric characters, underscores, and hyphens" in str(exc_info.value)

def test_permission_create_schema():
    data = {
        "name": "delete_user",
        "description": "Permission to delete a user"
    }
    schema = PermissionCreateSchema(**data)
    assert schema.name == "delete_user"
    assert schema.description == "Permission to delete a user"

def test_permission_update_schema():
    data = {
        "name": "update_user",
        "description": "Updated permission to modify a user"
    }
    schema = PermissionUpdateSchema(**data)
    assert schema.name == "update_user"
    assert schema.description == "Updated permission to modify a user"

    # Test partial update
    partial_data = {"description": "Partially updated description"}
    partial_schema = PermissionUpdateSchema(**partial_data)
    assert partial_schema.name is None
    assert partial_schema.description == "Partially updated description"

def test_permission_schema():
    data = {
        "id": 1,
        "name": "read_user",
        "description": "Permission to read user information"
    }
    schema = PermissionSchema(**data)
    assert schema.id == 1
    assert schema.name == "read_user"
    assert schema.description == "Permission to read user information"

def test_permission_schema_from_attributes(db_session, test_permission):
    schema = PermissionSchema.model_validate(test_permission)
    assert schema.id == test_permission.id
    assert schema.name == test_permission.name
    assert schema.description == test_permission.description
