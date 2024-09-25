# filename: backend/tests/test_crud/test_crud_roles.py

import pytest
from sqlalchemy.exc import IntegrityError

from backend.app.crud.crud_permissions import create_permission_in_db
from backend.app.crud.crud_roles import (
    create_role_in_db,
    create_role_to_permission_association_in_db,
    delete_role_from_db,
    delete_role_to_permission_association_from_db,
    read_default_role_from_db,
    read_permissions_for_role_from_db,
    read_role_by_name_from_db,
    read_role_from_db,
    read_roles_from_db,
    read_users_for_role_from_db,
    update_role_in_db,
)
from backend.app.crud.crud_user import create_user_in_db


def test_create_role(db_session, test_role_data):
    role = create_role_in_db(db_session, test_role_data)
    assert role.name == test_role_data["name"]
    assert role.description == test_role_data["description"]


def test_read_role(db_session, test_role_data):
    role = create_role_in_db(db_session, test_role_data)
    read_role = read_role_from_db(db_session, role.id)
    assert read_role.id == role.id
    assert read_role.name == role.name


def test_read_role_by_name(db_session, test_role_data):
    role = create_role_in_db(db_session, test_role_data)
    read_role = read_role_by_name_from_db(db_session, role.name)
    assert read_role.id == role.id
    assert read_role.name == role.name


def test_read_roles(db_session, test_role_data):
    create_role_in_db(db_session, test_role_data)
    roles = read_roles_from_db(db_session)
    assert len(roles) > 0


def test_update_role(db_session, test_role_data):
    role = create_role_in_db(db_session, test_role_data)
    updated_data = {"description": "Updated description"}
    updated_role = update_role_in_db(db_session, role.id, updated_data)
    assert updated_role.description == "Updated description"


def test_delete_role(db_session, test_role_data):
    # Create a default role first
    default_role_data = {**test_role_data, "name": "Default Role", "default": True}
    created_default_role = create_role_in_db(db_session, default_role_data)
    assert created_default_role.default is True

    # Now create and delete the test role
    role = create_role_in_db(db_session, test_role_data)
    assert role.default is False
    assert delete_role_from_db(db_session, role.id) is True
    assert read_role_from_db(db_session, role.id) is None


def test_create_role_to_permission_association(
    db_session, test_role_data, test_schema_permission
):
    role = create_role_in_db(db_session, test_role_data)
    permission = create_permission_in_db(
        db_session, test_schema_permission.model_dump()
    )
    assert (
        create_role_to_permission_association_in_db(db_session, role.id, permission.id)
        is True
    )


def test_delete_role_to_permission_association(
    db_session, test_role_data, test_schema_permission
):
    role = create_role_in_db(db_session, test_role_data)
    permission = create_permission_in_db(
        db_session, test_schema_permission.model_dump()
    )
    create_role_to_permission_association_in_db(db_session, role.id, permission.id)
    assert (
        delete_role_to_permission_association_from_db(
            db_session, role.id, permission.id
        )
        is True
    )


def test_read_permissions_for_role(db_session, test_role_data, test_schema_permission):
    role = create_role_in_db(db_session, test_role_data)
    initial_permissions = read_permissions_for_role_from_db(db_session, role.id)

    permission = create_permission_in_db(
        db_session, test_schema_permission.model_dump()
    )
    create_role_to_permission_association_in_db(db_session, role.id, permission.id)

    updated_permissions = read_permissions_for_role_from_db(db_session, role.id)
    assert len(updated_permissions) == len(initial_permissions) + 1
    assert permission.id in [p.id for p in updated_permissions]


def test_read_users_for_role(db_session, test_role_data, test_user_data):
    role = create_role_in_db(db_session, test_role_data)
    user_data = test_user_data
    user_data["role_id"] = role.id
    user = create_user_in_db(db_session, user_data)
    users = read_users_for_role_from_db(db_session, role.id)
    assert len(users) == 1
    assert users[0].id == user.id


def test_create_duplicate_role(db_session, test_role_data):
    create_role_in_db(db_session, test_role_data)
    with pytest.raises(IntegrityError):
        create_role_in_db(db_session, test_role_data)


def test_read_nonexistent_role(db_session):
    nonexistent_id = 9999
    assert read_role_from_db(db_session, nonexistent_id) is None


def test_update_nonexistent_role(db_session):
    nonexistent_id = 9999
    updated_data = {"description": "Updated description"}
    assert update_role_in_db(db_session, nonexistent_id, updated_data) is None


def test_delete_nonexistent_role(db_session):
    nonexistent_id = 9999
    assert delete_role_from_db(db_session, nonexistent_id) is False


def test_create_role_with_default_true(db_session, test_role_data):
    role_data = {**test_role_data, "default": True}
    role = create_role_in_db(db_session, role_data)
    assert role.default is True


def test_update_role_default_status(db_session, test_role_data):
    role = create_role_in_db(db_session, test_role_data)
    updated_data = {"default": True}
    updated_role = update_role_in_db(db_session, role.id, updated_data)
    assert updated_role.default is True


def test_read_default_role(db_session, test_role_data):
    default_role_data = {**test_role_data, "default": True}
    created_default_role = create_role_in_db(db_session, default_role_data)
    assert created_default_role.default is True
    read_role = read_role_from_db(db_session, created_default_role.id)
    assert read_role.default is True
    default_role = read_default_role_from_db(db_session)
    assert default_role is not None
    assert default_role.default is True


def test_create_multiple_default_roles(db_session, test_role_data):
    role_data1 = {**test_role_data, "name": "Default Role 1", "default": True}
    role_data2 = {**test_role_data, "name": "Default Role 2", "default": True}
    create_role_in_db(db_session, role_data1)
    with pytest.raises(IntegrityError):
        create_role_in_db(db_session, role_data2)


def test_update_role_name(db_session, test_role_data):
    role = create_role_in_db(db_session, test_role_data)
    new_name = "Updated Role Name"
    updated_data = {"name": new_name}
    updated_role = update_role_in_db(db_session, role.id, updated_data)
    assert updated_role.name == new_name


def test_read_roles_pagination(db_session, test_role_data):
    for i in range(5):
        create_role_in_db(db_session, {**test_role_data, "name": f"Role {i}"})

    page1 = read_roles_from_db(db_session, skip=0, limit=2)
    page2 = read_roles_from_db(db_session, skip=2, limit=2)

    assert len(page1) == 2
    assert len(page2) == 2
    assert page1[0].id != page2[0].id


def test_delete_role_cascade(
    db_session, test_role_data, test_schema_permission, test_user_data
):
    # Create a default role first
    default_role_data = {**test_role_data, "name": "Default Role", "default": True}
    created_default_role = create_role_in_db(db_session, default_role_data)
    assert created_default_role.default is True

    user_role_data = {**test_role_data, "name": "User Role", "default": False}
    user_role = create_role_in_db(db_session, user_role_data)
    assert user_role.default is False
    
    permission = create_permission_in_db(
        db_session, test_schema_permission.model_dump()
    )
    create_role_to_permission_association_in_db(db_session, user_role.id, permission.id)

    user_data = {**test_user_data, "role_id": user_role.id}
    created_user = create_user_in_db(db_session, user_data)
    assert created_user.role_id == user_role.id

    delete_role_from_db(db_session, user_role.id)

    assert read_role_from_db(db_session, user_role.id) is None
    assert read_permissions_for_role_from_db(db_session, user_role.id) == []
    assert read_users_for_role_from_db(db_session, user_role.id) == []


def test_create_role_with_permissions(
    db_session, test_role_data, test_schema_permission
):
    permission = create_permission_in_db(
        db_session, test_schema_permission.model_dump()
    )
    role_data = {**test_role_data, "permissions": [permission.name]}
    role = create_role_in_db(db_session, role_data)

    role_permissions = read_permissions_for_role_from_db(db_session, role.id)
    assert len(role_permissions) == 1
    assert role_permissions[0].id == permission.id


def test_update_role_permissions(db_session, test_role_data, test_schema_permission):
    role = create_role_in_db(db_session, test_role_data)
    permission1 = create_permission_in_db(
        db_session, test_schema_permission.model_dump()
    )
    permission2 = create_permission_in_db(
        db_session,
        {**test_schema_permission.model_dump(), "name": "another_permission"},
    )

    updated_data = {"permissions": [permission1.name, permission2.name]}
    updated_role = update_role_in_db(db_session, role.id, updated_data)

    role_permissions = read_permissions_for_role_from_db(db_session, updated_role.id)
    assert len(role_permissions) == 2
    assert {p.id for p in role_permissions} == {permission1.id, permission2.id}
