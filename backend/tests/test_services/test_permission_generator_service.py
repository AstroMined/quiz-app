# filename: backend/tests/test_services/test_permission_generator_service.py

import pytest
from fastapi import FastAPI
from backend.app.services.permission_generator_service import generate_permissions, ensure_permissions_in_db
from backend.app.models.permissions import PermissionModel
from backend.app.core.config import settings_core

def test_generate_permissions():
    app = FastAPI()

    @app.get("/test")
    def test_route():
        pass

    @app.post("/protected")
    def protected_route():
        pass

    # Add an unprotected endpoint
    settings_core.UNPROTECTED_ENDPOINTS = ["_test"]

    permissions = generate_permissions(app)

    assert "read_test" not in permissions  # This should be excluded as it's in UNPROTECTED_ENDPOINTS
    assert "create_protected" in permissions

def test_ensure_permissions_in_db(db_session):
    # Create some existing permissions
    existing_permission = PermissionModel(name="existing_permission")
    db_session.add(existing_permission)
    db_session.commit()

    # Generate new permissions
    new_permissions = {"existing_permission", "new_permission1", "new_permission2"}

    ensure_permissions_in_db(db_session, new_permissions)

    # Check if all permissions are in the database
    db_permissions = set(p.name for p in db_session.query(PermissionModel).all())
    assert db_permissions == new_permissions

    # Check that no duplicate permissions were created
    assert db_session.query(PermissionModel).count() == len(new_permissions)

# You might need to add more tests depending on the complexity of your FastAPI routes
# and any edge cases in your permission generation logic