# filename: backend/tests/fixtures/models/user_fixtures.py

import random
import string
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


@pytest.fixture(scope="function")
def test_permission(db_session):
    """Create a single test permission."""
    permission = PermissionModel(
        name="test_permission", description="A test permission"
    )
    db_session.add(permission)
    db_session.commit()
    return permission


@pytest.fixture(scope="function")
def test_model_permissions(db_session):
    """Create all model-based permissions for the application."""
    permissions = generate_permissions(app)
    ensure_permissions_in_db(db_session, permissions)
    db_permissions = db_session.query(PermissionModel).all()
    return db_permissions


@pytest.fixture(scope="function")
def test_model_role(db_session, test_model_permissions):
    """Create a test role with all permissions."""
    role = RoleModel(name="test_role", description="Test Role", default=False)
    role.permissions.extend(test_model_permissions)
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


@pytest.fixture(scope="function")
def test_model_default_role(db_session, test_model_permissions):
    """Create a default test role with all permissions."""
    role = RoleModel(
        name="test_default_role", description="Test Default Role", default=True
    )
    role.permissions.extend(test_model_permissions)
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


@pytest.fixture(scope="function")
def test_random_username():
    """Generate a random username for testing."""
    random_username = "test.user_" + "".join(
        random.choices(string.ascii_letters + string.digits, k=5)
    )
    return random_username.lower()


@pytest.fixture(scope="function")
def test_model_user(db_session, test_random_username, test_model_role):
    """Create a test user with admin privileges."""
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
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_model_group(db_session, test_model_user):
    """Create a test group."""
    group = GroupModel(
        name="Test Group",
        description="This is a test group",
        creator_id=test_model_user.id,
    )
    db_session.add(group)
    db_session.commit()
    db_session.refresh(group)
    return group


@pytest.fixture(scope="function")
def test_model_user_with_group(db_session, test_model_user, test_model_group):
    """Create a test user associated with a group."""
    association = UserToGroupAssociation(
        user_id=test_model_user.id, group_id=test_model_group.id
    )
    db_session.add(association)
    db_session.commit()
    return test_model_user