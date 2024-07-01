# filename: tests/test_crud/test_crud_roles.py

import pytest
from fastapi import HTTPException
from app.crud.crud_roles import create_role_crud, read_role_crud, read_roles_crud, update_role_crud, delete_role_crud
from app.schemas.roles import RoleCreateSchema, RoleUpdateSchema
from app.services.logging_service import logger
from app.crud.crud_permissions import read_permissions_crud


def test_create_role_crud(db_session, test_permissions):
    read_permissions = read_permissions_crud(db_session, limit=2)  # Retrieve the first two permissions from the database
    logger.debug("Permissions read: %s", read_permissions)
    permissions_id_list = [p.id for p in read_permissions]
    logger.debug("Permissions list: %s", permissions_id_list)
    permissions_name_list = [p.name for p in read_permissions]
    logger.debug("Permissions name list: %s", permissions_name_list)
    role_data = RoleCreateSchema(name="Test Role", description="Test role description", permissions=permissions_name_list)
    logger.debug("Role data: %s", role_data)
    role = create_role_crud(db_session, role_data)
    logger.debug("Role created: %s", role)
    assert role.name == "Test Role"
    assert role.description == "Test role description"
    logger.debug("Role permissions: %s", role.permissions)
    assert len(role.permissions) == 2

def test_read_role_crud(db_session):
    role_data = RoleCreateSchema(name="Test Role", description="Test role description", permissions=[])
    created_role = create_role_crud(db_session, role_data)
    
    read_role = read_role_crud(db_session, created_role.id)
    assert read_role.id == created_role.id
    assert read_role.name == "Test Role"

def test_read_role_crud_not_found(db_session):
    with pytest.raises(HTTPException) as exc_info:
        read_role_crud(db_session, 999)  # Assuming 999 is not a valid role id
    assert exc_info.value.status_code == 404

def test_read_roles_crud(db_session):
    role_data1 = RoleCreateSchema(name="Test Role 1", description="Test role description 1", permissions=[])
    role_data2 = RoleCreateSchema(name="Test Role 2", description="Test role description 2", permissions=[])
    create_role_crud(db_session, role_data1)
    create_role_crud(db_session, role_data2)

    roles = read_roles_crud(db_session)
    assert len(roles) >= 2

def test_update_role_crud(db_session, test_permissions):
    permissions = read_permissions_crud(db_session, limit=2)  # Retrieve the first two permissions from the database
    logger.debug("Permissions read: %s", permissions)
    permissions_id_list = [p.id for p in permissions]
    logger.debug("Permissions list: %s", permissions_id_list)
    permissions_name_list = [p.name for p in permissions]
    logger.debug("Permissions name list: %s", permissions_name_list)
    role_data = RoleCreateSchema(name="Test Role", description="Test role description", permissions=permissions_name_list)
    logger.debug("Role data: %s", role_data)
    created_role = create_role_crud(db_session, role_data)
    logger.debug("Created role: %s", created_role)
    logger.debug("Created role permissions: %s", created_role.permissions)

    db_session.rollback()  # Roll back the previous transaction

    update_data = RoleUpdateSchema(name="Updated Role", description="Updated description", permissions=permissions_name_list)
    logger.debug("Update data: %s", update_data)
    updated_role = update_role_crud(db_session, created_role.id, update_data)
    logger.debug("Updated role: %s", updated_role)
    logger.debug("Updated role permissions: %s", updated_role.permissions)

    assert updated_role.name == "Updated Role"
    assert updated_role.description == "Updated description"
    assert len(updated_role.permissions) == 2

def test_delete_role_crud(db_session):
    role_data = RoleCreateSchema(name="Test Role", description="Test role description", permissions=[])
    created_role = create_role_crud(db_session, role_data)

    assert delete_role_crud(db_session, created_role.id) == True

    with pytest.raises(HTTPException) as exc_info:
        read_role_crud(db_session, created_role.id)
    assert exc_info.value.status_code == 404
