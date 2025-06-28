# filename: backend/tests/crud/test_crud_user.py

from backend.app.crud.crud_groups import create_group_in_db
from backend.app.crud.crud_question_sets import create_question_set_in_db
from backend.app.crud.crud_roles import create_role_in_db
from backend.app.crud.crud_user import (
    create_user_in_db,
    create_user_to_group_association_in_db,
    delete_user_from_db,
    delete_user_to_group_association_from_db,
    read_created_question_sets_for_user_from_db,
    read_groups_for_user_from_db,
    read_role_for_user_from_db,
    read_user_by_email_from_db,
    read_user_by_username_from_db,
    read_user_from_db,
    read_users_from_db,
    update_user_in_db,
)


def test_create_user(db_session, test_user_data):
    user = create_user_in_db(db_session, test_user_data)
    assert user.username == test_user_data["username"]
    assert user.email == test_user_data["email"]


def test_read_user(db_session, test_user_data):
    user = create_user_in_db(db_session, test_user_data)
    read_user = read_user_from_db(db_session, user.id)
    assert read_user.id == user.id
    assert read_user.username == user.username


def test_read_user_by_username(db_session, test_user_data):
    user = create_user_in_db(db_session, test_user_data)
    read_user = read_user_by_username_from_db(db_session, user.username)
    assert read_user.id == user.id
    assert read_user.username == user.username


def test_read_user_by_email(db_session, test_user_data):
    user = create_user_in_db(db_session, test_user_data)
    read_user = read_user_by_email_from_db(db_session, user.email)
    assert read_user.id == user.id
    assert read_user.email == user.email


def test_read_users(db_session, test_user_data):
    create_user_in_db(db_session, test_user_data)
    users = read_users_from_db(db_session)
    assert len(users) > 0


def test_update_user(db_session, test_user_data):
    user = create_user_in_db(db_session, test_user_data)
    updated_data = {"email": "updated@example.com"}
    updated_user = update_user_in_db(db_session, user.id, updated_data)
    assert updated_user.email == "updated@example.com"


def test_delete_user(db_session, test_user_data):
    user = create_user_in_db(db_session, test_user_data)
    assert delete_user_from_db(db_session, user.id) is True
    assert read_user_from_db(db_session, user.id) is None


def test_create_user_to_group_association(db_session, test_user_data, test_group_data):
    user = create_user_in_db(db_session, test_user_data)
    group = create_group_in_db(db_session, test_group_data)
    assert create_user_to_group_association_in_db(db_session, user.id, group.id) is True


def test_delete_user_to_group_association(db_session, test_user_data, test_group_data):
    user = create_user_in_db(db_session, test_user_data)
    group = create_group_in_db(db_session, test_group_data)
    create_user_to_group_association_in_db(db_session, user.id, group.id)
    assert (
        delete_user_to_group_association_from_db(db_session, user.id, group.id) is True
    )


def test_read_groups_for_user(db_session, test_user_data, test_group_data):
    user = create_user_in_db(db_session, test_user_data)
    group = create_group_in_db(db_session, test_group_data)
    create_user_to_group_association_in_db(db_session, user.id, group.id)
    groups = read_groups_for_user_from_db(db_session, user.id)
    assert len(groups) == 1
    assert groups[0].id == group.id


def test_read_role_for_user(db_session, test_user_data, test_role_data):
    role = create_role_in_db(db_session, test_role_data)
    user_data = test_user_data
    user_data["role_id"] = role.id
    user = create_user_in_db(db_session, user_data)
    user_role = read_role_for_user_from_db(db_session, user.id)
    assert user_role.id == role.id


def test_read_created_question_sets_for_user(
    db_session, test_user_data, test_question_set_data
):
    user = create_user_in_db(db_session, test_user_data)
    question_set_data = test_question_set_data
    question_set_data["creator_id"] = user.id
    question_set = create_question_set_in_db(db_session, question_set_data)
    created_sets = read_created_question_sets_for_user_from_db(db_session, user.id)
    assert len(created_sets) == 1
    assert created_sets[0].id == question_set.id
