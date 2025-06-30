# filename: backend/tests/test_services/test_permission_generator_service.py

import pytest
from fastapi import FastAPI

from backend.app.core.config import settings_core
from backend.app.models.permissions import PermissionModel
from backend.app.services.permission_generator_service import (
    ensure_permissions_in_db,
    generate_permissions,
)


def test_generate_permissions():
    app = FastAPI()

    @app.get("/test")
    def test_route():
        pass

    @app.post("/protected")
    def protected_route():
        pass

    # Add an unprotected endpoint
    settings_core.UNPROTECTED_ENDPOINTS = ["test"]

    permissions = generate_permissions(app)

    assert (
        "read_test" not in permissions
    )  # This should be excluded as it's in UNPROTECTED_ENDPOINTS
    assert "create_protected" in permissions


def test_ensure_permissions_in_db(db_session):
    # Get initial permission count (may include reference data)
    initial_permissions = set(p.name for p in db_session.query(PermissionModel).all())
    initial_count = len(initial_permissions)
    
    # Create some existing permissions
    existing_permission = PermissionModel(name="existing_permission")
    db_session.add(existing_permission)
    db_session.commit()

    # Generate new permissions
    new_permissions = {"existing_permission", "new_permission1", "new_permission2"}

    ensure_permissions_in_db(db_session, new_permissions)

    # Check if all our test permissions are in the database
    db_permissions = set(p.name for p in db_session.query(PermissionModel).all())
    for permission in new_permissions:
        assert permission in db_permissions, f"Permission '{permission}' not found in database"

    # Check that the count increased by the right amount 
    # We added "existing_permission" explicitly, then ensure_permissions_in_db added new_permission1 and new_permission2
    expected_new_count = initial_count + 3  # existing_permission + new_permission1 + new_permission2
    actual_count = db_session.query(PermissionModel).count()
    assert actual_count == expected_new_count, f"Expected {expected_new_count} permissions, got {actual_count}"


def test_permission_generation_patterns():
    """Test permission generation for various route patterns."""
    app = FastAPI()

    @app.get("/simple")
    def simple_route():
        pass

    @app.post("/nested/path")
    def nested_route():
        pass

    @app.put("/with/{param}")
    def parameterized_route():
        pass

    @app.delete("/api/v1/users")
    def api_route():
        pass

    @app.get("/")
    def root_route():
        pass

    permissions = generate_permissions(app)

    # Test expected permission formats
    assert "read_simple" in permissions
    assert "create_nested_path" in permissions
    assert "update_with_param" in permissions
    assert "delete_api_v1_users" in permissions
    assert "read_" in permissions  # Root path case

    # Ensure no double underscores
    for permission in permissions:
        assert "__" not in permission, f"Permission '{permission}' contains double underscores"


def test_permission_edge_cases():
    """Test permission generation for edge cases and special characters."""
    app = FastAPI()

    @app.get("/path-with-dashes")
    def dash_route():
        pass

    @app.post("/path.with.dots")
    def dot_route():
        pass

    @app.put("/multiple/{param1}/{param2}")
    def multi_param_route():
        pass

    @app.delete("/trailing/slash/")
    def trailing_slash_route():
        pass

    permissions = generate_permissions(app)

    # Test that special characters are handled
    expected_permissions = [
        "read_path-with-dashes",
        "create_path.with.dots", 
        "update_multiple_param1_param2",
        "delete_trailing_slash"  # Trailing slash gets stripped
    ]

    for expected in expected_permissions:
        assert expected in permissions, f"Expected permission '{expected}' not found"

    # Ensure no double underscores in any permission
    for permission in permissions:
        assert "__" not in permission, f"Permission '{permission}' contains double underscores"


def test_unprotected_endpoints_exclusion():
    """Test that unprotected endpoints are properly excluded."""
    app = FastAPI()

    @app.get("/public")
    def public_route():
        pass

    @app.post("/private")
    def private_route():
        pass

    # Configure unprotected endpoints
    settings_core.UNPROTECTED_ENDPOINTS = ["public", "docs", "openapi.json"]

    permissions = generate_permissions(app)

    # Public endpoint should be excluded
    assert "read_public" not in permissions
    # Private endpoint should be included
    assert "create_private" in permissions
