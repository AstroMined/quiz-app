# filename: backend/tests/integration/models/test_permission_model.py

import pytest
from sqlalchemy.exc import IntegrityError

from backend.app.models.permissions import PermissionModel
from backend.app.models.roles import RoleModel


def test_permission_creation(db_session):
    permission = PermissionModel(name="create_user", description="Permission to create a new user")
    db_session.add(permission)
    db_session.commit()

    assert permission.id is not None
    assert permission.name == "create_user"
    assert permission.description == "Permission to create a new user"


def test_permission_unique_name(db_session):
    permission1 = PermissionModel(name="delete_user", description="Permission to delete a user")
    db_session.add(permission1)
    db_session.commit()

    with pytest.raises(IntegrityError):
        permission2 = PermissionModel(name="delete_user", description="Another delete permission")
        db_session.add(permission2)
        db_session.commit()
    db_session.rollback()


def test_permission_role_relationship(db_session):
    permission = PermissionModel(name="read_user", description="Permission to read user information")
    role = RoleModel(name="User Reader", description="Role for reading users")
    permission.roles.append(role)
    db_session.add_all([permission, role])
    db_session.commit()

    assert role in permission.roles
    assert permission in role.permissions


def test_permission_required_fields(db_session):
    # Test missing name
    with pytest.raises(IntegrityError):
        permission = PermissionModel(description="Permission without name")
        db_session.add(permission)
        db_session.commit()
    db_session.rollback()


def test_permission_repr(db_session):
    permission = PermissionModel(name="update_user", description="Permission to update user information")
    db_session.add(permission)
    db_session.commit()

    expected_repr = f"<PermissionModel(id={permission.id}, name='update_user')>"
    assert repr(permission) == expected_repr


def test_permission_schema_from_attributes(db_session, test_permission):
    from backend.app.schemas.permissions import PermissionSchema
    
    schema = PermissionSchema.model_validate(test_permission)
    assert schema.id == test_permission.id
    assert schema.name == test_permission.name
    assert schema.description == test_permission.description