# filename: backend/tests/test_crud/test_crud_permissions.py

import pytest

from backend.app.crud.crud_permissions import (
    create_permission_in_db,
    create_role_to_permission_association_in_db,
    delete_permission_from_db,
    delete_role_to_permission_association_from_db,
    read_permission_by_name_from_db,
    read_permission_from_db,
    read_permissions_from_db,
    read_roles_for_permission_from_db,
    update_permission_in_db,
)
from backend.app.crud.crud_roles import create_role_in_db


def test_create_permission(db_session, test_schema_permission):
    permission = create_permission_in_db(
        db_session, test_schema_permission.model_dump()
    )
    assert permission.name == test_schema_permission.name
    assert permission.description == test_schema_permission.description


def test_read_permission(db_session, test_schema_permission):
    permission = create_permission_in_db(
        db_session, test_schema_permission.model_dump()
    )
    read_permission = read_permission_from_db(db_session, permission.id)
    assert read_permission.id == permission.id
    assert read_permission.name == permission.name


def test_read_permission_by_name(db_session, test_schema_permission):
    permission = create_permission_in_db(
        db_session, test_schema_permission.model_dump()
    )
    read_permission = read_permission_by_name_from_db(db_session, permission.name)
    assert read_permission.id == permission.id
    assert read_permission.name == permission.name


def test_read_permissions(db_session, test_schema_permission):
    create_permission_in_db(db_session, test_schema_permission.model_dump())
    permissions = read_permissions_from_db(db_session)
    assert len(permissions) > 0


def test_update_permission(db_session, test_schema_permission):
    permission = create_permission_in_db(
        db_session, test_schema_permission.model_dump()
    )
    updated_data = {"description": "Updated description"}
    updated_permission = update_permission_in_db(
        db_session, permission.id, updated_data
    )
    assert updated_permission.description == "Updated description"


def test_delete_permission(db_session, test_schema_permission):
    permission = create_permission_in_db(
        db_session, test_schema_permission.model_dump()
    )
    assert delete_permission_from_db(db_session, permission.id) is True
    assert read_permission_from_db(db_session, permission.id) is None


def test_create_role_to_permission_association(
    db_session, test_schema_permission, test_schema_role
):
    permission = create_permission_in_db(
        db_session, test_schema_permission.model_dump()
    )
    role = create_role_in_db(db_session, test_schema_role.model_dump())
    assert (
        create_role_to_permission_association_in_db(db_session, role.id, permission.id)
        is True
    )


def test_delete_role_to_permission_association(
    db_session, test_schema_permission, test_schema_role
):
    permission = create_permission_in_db(
        db_session, test_schema_permission.model_dump()
    )
    role = create_role_in_db(db_session, test_schema_role.model_dump())
    create_role_to_permission_association_in_db(db_session, role.id, permission.id)
    assert (
        delete_role_to_permission_association_from_db(
            db_session, role.id, permission.id
        )
        is True
    )


def test_read_roles_for_permission(
    db_session, test_schema_permission, test_schema_role
):
    permission = create_permission_in_db(
        db_session, test_schema_permission.model_dump()
    )
    role = create_role_in_db(db_session, test_schema_role.model_dump())
    create_role_to_permission_association_in_db(db_session, role.id, permission.id)
    roles = read_roles_for_permission_from_db(db_session, permission.id)
    assert len(roles) == 1
    assert roles[0].id == role.id


def test_create_duplicate_permission(db_session, test_schema_permission):
    create_permission_in_db(db_session, test_schema_permission.model_dump())
    with pytest.raises(Exception):  # Adjust the exception type if needed
        create_permission_in_db(db_session, test_schema_permission.model_dump())


def test_read_nonexistent_permission(db_session):
    nonexistent_id = 9999
    assert read_permission_from_db(db_session, nonexistent_id) is None


def test_read_nonexistent_permission_by_name(db_session):
    nonexistent_name = "nonexistent_permission"
    assert read_permission_by_name_from_db(db_session, nonexistent_name) is None


def test_update_nonexistent_permission(db_session):
    nonexistent_id = 9999
    updated_data = {"description": "Updated description"}
    assert update_permission_in_db(db_session, nonexistent_id, updated_data) is None


def test_delete_nonexistent_permission(db_session):
    nonexistent_id = 9999
    assert delete_permission_from_db(db_session, nonexistent_id) is False


def test_create_multiple_permissions(db_session, test_schema_permission):
    permission1 = create_permission_in_db(
        db_session, test_schema_permission.model_dump()
    )
    permission2 = create_permission_in_db(
        db_session,
        {**test_schema_permission.model_dump(), "name": "another_permission"},
    )
    permissions = read_permissions_from_db(db_session)
    assert len(permissions) == 2
    assert {p.id for p in permissions} == {permission1.id, permission2.id}


def test_update_permission_name(db_session, test_schema_permission):
    permission = create_permission_in_db(
        db_session, test_schema_permission.model_dump()
    )
    new_name = "updated_permission_name"
    updated_permission = update_permission_in_db(
        db_session, permission.id, {"name": new_name}
    )
    assert updated_permission.name == new_name
    assert read_permission_by_name_from_db(db_session, new_name) is not None


def test_delete_permission_cascade(
    db_session, test_schema_permission, test_schema_role
):
    permission = create_permission_in_db(
        db_session, test_schema_permission.model_dump()
    )
    role = create_role_in_db(db_session, test_schema_role.model_dump())
    create_role_to_permission_association_in_db(db_session, role.id, permission.id)

    delete_permission_from_db(db_session, permission.id)

    assert read_permission_from_db(db_session, permission.id) is None
    assert read_roles_for_permission_from_db(db_session, permission.id) == []


def test_read_permissions_pagination(db_session, test_schema_permission):
    for i in range(5):
        create_permission_in_db(
            db_session,
            {**test_schema_permission.model_dump(), "name": f"permission_{i}"},
        )

    permissions_page1 = read_permissions_from_db(db_session, skip=0, limit=2)
    permissions_page2 = read_permissions_from_db(db_session, skip=2, limit=2)

    assert len(permissions_page1) == 2
    assert len(permissions_page2) == 2
    assert permissions_page1[0].id != permissions_page2[0].id


def test_create_role_to_permission_association_idempotent(
    db_session, test_schema_permission, test_schema_role
):
    permission = create_permission_in_db(
        db_session, test_schema_permission.model_dump()
    )
    role = create_role_in_db(db_session, test_schema_role.model_dump())

    first_association = create_role_to_permission_association_in_db(
        db_session, role.id, permission.id
    )
    assert first_association is True
    second_association = create_role_to_permission_association_in_db(
        db_session, role.id, permission.id
    )
    assert second_association is False

    roles = read_roles_for_permission_from_db(db_session, permission.id)
    assert len(roles) == 1
