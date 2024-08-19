# filename: backend/tests/crud/test_crud_permissions.py

import pytest

from backend.app.crud.crud_permissions import (
    create_permission_in_db, create_role_to_permission_association_in_db,
    delete_permission_from_db, delete_role_to_permission_association_from_db,
    read_permission_by_name_from_db, read_permission_from_db,
    read_permissions_from_db, read_roles_for_permission_from_db,
    update_permission_in_db)
from backend.app.crud.crud_roles import create_role_in_db


def test_create_permission(db_session, test_schema_permission):
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    assert permission.name == test_schema_permission.name
    assert permission.description == test_schema_permission.description

def test_read_permission(db_session, test_schema_permission):
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    read_permission = read_permission_from_db(db_session, permission.id)
    assert read_permission.id == permission.id
    assert read_permission.name == permission.name

def test_read_permission_by_name(db_session, test_schema_permission):
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    read_permission = read_permission_by_name_from_db(db_session, permission.name)
    assert read_permission.id == permission.id
    assert read_permission.name == permission.name

def test_read_permissions(db_session, test_schema_permission):
    create_permission_in_db(db_session, test_schema_permission.model_dump())
    permissions = read_permissions_from_db(db_session)
    assert len(permissions) > 0

def test_update_permission(db_session, test_schema_permission):
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    updated_data = {"description": "Updated description"}
    updated_permission = update_permission_in_db(db_session, permission.id, updated_data)
    assert updated_permission.description == "Updated description"

def test_delete_permission(db_session, test_schema_permission):
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    assert delete_permission_from_db(db_session, permission.id) is True
    assert read_permission_from_db(db_session, permission.id) is None

def test_create_role_to_permission_association(db_session, test_schema_permission, test_schema_role):
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    role = create_role_in_db(db_session, test_schema_role.model_dump())
    assert create_role_to_permission_association_in_db(db_session, role.id, permission.id) is True

def test_delete_role_to_permission_association(db_session, test_schema_permission, test_schema_role):
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    role = create_role_in_db(db_session, test_schema_role.model_dump())
    create_role_to_permission_association_in_db(db_session, role.id, permission.id)
    assert delete_role_to_permission_association_from_db(db_session, role.id, permission.id) is True

def test_read_roles_for_permission(db_session, test_schema_permission, test_schema_role):
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    role = create_role_in_db(db_session, test_schema_role.model_dump())
    create_role_to_permission_association_in_db(db_session, role.id, permission.id)
    roles = read_roles_for_permission_from_db(db_session, permission.id)
    assert len(roles) == 1
    assert roles[0].id == role.id
