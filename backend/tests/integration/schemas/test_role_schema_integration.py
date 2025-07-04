# filename: backend/tests/integration/schemas/test_role_schema_integration.py

import pytest

from backend.app.schemas.roles import RoleSchema


def test_role_schema_from_attributes(db_session, admin_role):
    """Test RoleSchema validation with real SQLAlchemy model (integration test)."""
    # Re-attach the model to the current session to avoid DetachedInstanceError
    role = db_session.merge(admin_role)
    
    # Force load relationships to avoid lazy loading issues
    _ = role.permissions
    
    schema = RoleSchema.model_validate(role)
    assert schema.id == role.id
    assert schema.name == role.name
    assert schema.description == role.description
    assert schema.default == role.default
    assert set(schema.permissions) == set(
        permission.name for permission in role.permissions
    )