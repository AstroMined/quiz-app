# filename: backend/tests/crud/test_crud_roles.py

from backend.app.crud.crud_permissions import create_permission_in_db
from backend.app.crud.crud_roles import (
    create_role_in_db, create_role_to_permission_association_in_db,
    delete_role_from_db, delete_role_to_permission_association_from_db,
    read_permissions_for_role_from_db, read_role_by_name_from_db,
    read_role_from_db, read_roles_from_db, read_users_for_role_from_db,
    update_role_in_db)
from backend.app.crud.crud_user import create_user_in_db


def test_create_role(db_session, test_schema_role):
    role = create_role_in_db(db_session, test_schema_role.model_dump())
    assert role.name == test_schema_role.name
    assert role.description == test_schema_role.description

def test_read_role(db_session, test_schema_role):
    role = create_role_in_db(db_session, test_schema_role.model_dump())
    read_role = read_role_from_db(db_session, role.id)
    assert read_role.id == role.id
    assert read_role.name == role.name

def test_read_role_by_name(db_session, test_schema_role):
    role = create_role_in_db(db_session, test_schema_role.model_dump())
    read_role = read_role_by_name_from_db(db_session, role.name)
    assert read_role.id == role.id
    assert read_role.name == role.name

def test_read_roles(db_session, test_schema_role):
    create_role_in_db(db_session, test_schema_role.model_dump())
    roles = read_roles_from_db(db_session)
    assert len(roles) > 0

def test_update_role(db_session, test_schema_role):
    role = create_role_in_db(db_session, test_schema_role.model_dump())
    updated_data = {"description": "Updated description"}
    updated_role = update_role_in_db(db_session, role.id, updated_data)
    assert updated_role.description == "Updated description"

def test_delete_role(db_session, test_schema_role):
    role = create_role_in_db(db_session, test_schema_role.model_dump())
    assert delete_role_from_db(db_session, role.id) is True
    assert read_role_from_db(db_session, role.id) is None

def test_create_role_to_permission_association(db_session, test_schema_role, test_schema_permission):
    role = create_role_in_db(db_session, test_schema_role.model_dump())
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    assert create_role_to_permission_association_in_db(db_session, role.id, permission.id) is True

def test_delete_role_to_permission_association(db_session, test_schema_role, test_schema_permission):
    role = create_role_in_db(db_session, test_schema_role.model_dump())
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    create_role_to_permission_association_in_db(db_session, role.id, permission.id)
    assert delete_role_to_permission_association_from_db(db_session, role.id, permission.id) is True

def test_read_permissions_for_role(db_session, test_schema_role, test_schema_permission):
    role = create_role_in_db(db_session, test_schema_role.model_dump())
    permission = create_permission_in_db(db_session, test_schema_permission.model_dump())
    create_role_to_permission_association_in_db(db_session, role.id, permission.id)
    permissions = read_permissions_for_role_from_db(db_session, role.id)
    assert len(permissions) == 1
    assert permissions[0].id == permission.id

def test_read_users_for_role(db_session, test_schema_role, test_schema_user):
    role = create_role_in_db(db_session, test_schema_role.model_dump())
    user_data = test_schema_user.model_dump()
    user_data['role_id'] = role.id
    user = create_user_in_db(db_session, user_data)
    users = read_users_for_role_from_db(db_session, role.id)
    assert len(users) == 1
    assert users[0].id == user.id
