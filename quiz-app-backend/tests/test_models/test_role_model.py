# filename: tests/test_models/test_role_model.py

import pytest
from sqlalchemy.exc import SQLAlchemyError
from app.models.permissions import PermissionModel
from app.models.roles import RoleModel


def test_role_permission_relationship(db_session):
    try:
        # Create a role and permissions
        role = RoleModel(name='Test Role', description='Test role description')
        permission1 = PermissionModel(name='Test Permission 1', description='Test permission 1 description')
        permission2 = PermissionModel(name='Test Permission 2', description='Test permission 2 description')

        role.permissions.extend([permission1, permission2])

        db_session.add(role)
        db_session.add(permission1)
        db_session.add(permission2)
        db_session.flush()  # This will assign IDs without committing the transaction


        # Retrieve the role and check its permissions
        retrieved_role = db_session.query(RoleModel).filter(RoleModel.name == 'Test Role').first()
        
        assert retrieved_role is not None, "Role not found in database"
        assert len(retrieved_role.permissions) == 2, f"Expected 2 permissions, found {len(retrieved_role.permissions)}"
        assert permission1 in retrieved_role.permissions, "Permission 1 not found in role's permissions"
        assert permission2 in retrieved_role.permissions, "Permission 2 not found in role's permissions"

        # Refresh the permissions to ensure they have the latest data
        db_session.refresh(permission1)
        db_session.refresh(permission2)


        # Check the reverse relationship
        assert role in permission1.roles, "Role not found in permission1's roles"
        assert role in permission2.roles, "Role not found in permission2's roles"

        db_session.commit()

    except SQLAlchemyError as e:
        pytest.fail(f"SQLAlchemy error occurred: {str(e)}")
    except AssertionError as e:
        pytest.fail(f"Assertion failed: {str(e)}")
    except Exception as e:
        pytest.fail(f"Unexpected error occurred: {str(e)}")