# filename: backend/tests/fixtures/models/user_fixtures.py

import random
import string
import uuid
import pytest

from backend.app.core.security import get_password_hash
from backend.app.models.permissions import PermissionModel
from backend.app.models.roles import RoleModel
from backend.app.models.users import UserModel
from backend.app.models.groups import GroupModel
from backend.app.models.associations import UserToGroupAssociation
from backend.app.services.permission_generator_service import (
    ensure_permissions_in_db,
    generate_permissions,
)
from backend.app.main import app

# Global cache for permission data initialization
_session_permissions_initialized = False


@pytest.fixture(scope="function")
def test_permission(db_session):
    """Create a single test permission."""
    permission = PermissionModel(
        name="test_permission", description="A test permission"
    )
    db_session.add(permission)
    db_session.commit()
    return permission


@pytest.fixture(scope="session")
def session_permissions(test_engine):
    """Create all model-based permissions once per test session."""
    global _session_permissions_initialized
    
    if not _session_permissions_initialized:
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(bind=test_engine)
        session = SessionLocal()
        try:
            permissions = generate_permissions(app)
            ensure_permissions_in_db(session, permissions)
            session.commit()
            _session_permissions_initialized = True
        finally:
            session.close()
    
    return True


@pytest.fixture(scope="function")
def test_model_permissions(db_session, session_permissions):
    """Get all model-based permissions from the session-initialized data."""
    db_permissions = db_session.query(PermissionModel).all()
    return db_permissions


@pytest.fixture(scope="function")
def test_model_role(db_session, test_model_permissions):
    """Create a test role with all permissions (will be rolled back after test)."""
    role = RoleModel(name="test_role", description="Test Role", default=False)
    role.permissions.extend(test_model_permissions)
    db_session.add(role)
    db_session.flush()  # Make available within transaction
    return role


@pytest.fixture(scope="function")
def test_model_default_role(db_session, test_model_permissions):
    """Create a default test role with all permissions (will be rolled back after test)."""
    role = RoleModel(
        name="test_default_role", description="Test Default Role", default=True
    )
    role.permissions.extend(test_model_permissions)
    db_session.add(role)
    db_session.flush()  # Make available within transaction
    return role


@pytest.fixture(scope="function")
def test_random_username():
    """Generate a truly unique username for testing using UUID."""
    unique_id = str(uuid.uuid4())[:8]  # Use first 8 chars of UUID
    random_username = f"test.user_{unique_id}"
    return random_username.lower()


@pytest.fixture(scope="function")
def test_model_user(db_session, test_random_username, test_model_role):
    """Create a test user with admin privileges (will be rolled back after test)."""
    email = f"{test_random_username}@example.com"
    hashed_password = get_password_hash("TestPassword123!")

    user = UserModel(
        username=test_random_username,
        email=email,
        hashed_password=hashed_password,
        is_active=True,
        is_admin=True,
        role_id=test_model_role.id,
    )

    db_session.add(user)
    db_session.flush()  # Make available within transaction
    return user


@pytest.fixture(scope="function")
def test_model_group(db_session, test_model_user):
    """Create a test group (will be rolled back after test)."""
    group = GroupModel(
        name="Test Group",
        description="This is a test group",
        creator_id=test_model_user.id,
    )
    db_session.add(group)
    db_session.flush()  # Make available within transaction
    return group


@pytest.fixture(scope="function")
def test_model_user_with_group(db_session, test_model_user, test_model_group):
    """Create a test user associated with a group (will be rolled back after test)."""
    association = UserToGroupAssociation(
        user_id=test_model_user.id, group_id=test_model_group.id
    )
    db_session.add(association)
    db_session.flush()  # Make available within transaction
    return test_model_user