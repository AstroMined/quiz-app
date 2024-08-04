# filename: tests/test_models/test_role_model.py

import pytest
from sqlalchemy.exc import SQLAlchemyError
from app.models.permissions import PermissionModel
from app.models.roles import RoleModel
from app.services.logging_service import logger


def test_role_permission_relationship(db_session):
    try:
        # Create a role and permissions
        role = RoleModel(name='Test Role', description='Test role description')
        permission1 = PermissionModel(name='Test Permission 1', description='Test permission 1 description')
        permission2 = PermissionModel(name='Test Permission 2', description='Test permission 2 description')
        
        logger.debug(f"Created role: {role}")
        logger.debug(f"Created permission1: {permission1}")
        logger.debug(f"Created permission2: {permission2}")

        role.permissions.extend([permission1, permission2])
        logger.debug(f"Role permissions after extend: {role.permissions}")

        db_session.add(role)
        db_session.add(permission1)
        db_session.add(permission2)
        db_session.flush()  # This will assign IDs without committing the transaction

        logger.debug(f"Role after flush: {role}")
        logger.debug(f"Permission1 after flush: {permission1}")
        logger.debug(f"Permission2 after flush: {permission2}")

        # Retrieve the role and check its permissions
        retrieved_role = db_session.query(RoleModel).filter(RoleModel.name == 'Test Role').first()
        logger.debug(f"Retrieved role: {retrieved_role}")
        
        assert retrieved_role is not None, "Role not found in database"
        assert len(retrieved_role.permissions) == 2, f"Expected 2 permissions, found {len(retrieved_role.permissions)}"
        assert permission1 in retrieved_role.permissions, "Permission 1 not found in role's permissions"
        assert permission2 in retrieved_role.permissions, "Permission 2 not found in role's permissions"

        # Refresh the permissions to ensure they have the latest data
        db_session.refresh(permission1)
        db_session.refresh(permission2)

        logger.debug(f"Permission1 roles: {permission1.roles}")
        logger.debug(f"Permission2 roles: {permission2.roles}")

        # Check the reverse relationship
        assert role in permission1.roles, "Role not found in permission1's roles"
        assert role in permission2.roles, "Role not found in permission2's roles"

        db_session.commit()

    except SQLAlchemyError as e:
        logger.exception(f"SQLAlchemy error occurred: {str(e)}")
        pytest.fail(f"SQLAlchemy error occurred: {str(e)}")
    except AssertionError as e:
        logger.exception(f"Assertion failed: {str(e)}")
        pytest.fail(f"Assertion failed: {str(e)}")
    except Exception as e:
        logger.exception(f"Unexpected error occurred: {str(e)}")
        pytest.fail(f"Unexpected error occurred: {str(e)}")