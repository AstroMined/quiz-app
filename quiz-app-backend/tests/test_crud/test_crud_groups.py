# filename: tests/crud/test_crud_groups.py

import pytest
from app.crud.crud_groups import (
    create_group_in_db,
    read_group_from_db,
    read_groups_from_db,
    update_group_in_db,
    delete_group_from_db,
    create_user_to_group_association_in_db,
    delete_user_to_group_association_from_db,
    create_question_set_to_group_association_in_db,
    delete_question_set_to_group_association_from_db,
    read_users_for_group_from_db,
    read_question_sets_for_group_from_db
)
from app.crud.crud_user import create_user_in_db
from app.crud.crud_question_sets import create_question_set_in_db

def test_create_group(db_session, test_schema_group):
    group = create_group_in_db(db_session, test_schema_group.model_dump())
    assert group.name == test_schema_group.name
    assert group.description == test_schema_group.description
    assert group.creator_id == test_schema_group.creator_id

def test_read_group(db_session, test_schema_group):
    group = create_group_in_db(db_session, test_schema_group.model_dump())
    read_group = read_group_from_db(db_session, group.id)
    assert read_group.id == group.id
    assert read_group.name == group.name

def test_read_groups(db_session, test_schema_group):
    create_group_in_db(db_session, test_schema_group.model_dump())
    groups = read_groups_from_db(db_session)
    assert len(groups) > 0

def test_update_group(db_session, test_schema_group):
    group = create_group_in_db(db_session, test_schema_group.model_dump())
    updated_data = {"name": "Updated Group", "description": "Updated description"}
    updated_group = update_group_in_db(db_session, group.id, updated_data)
    assert updated_group.name == "Updated Group"
    assert updated_group.description == "Updated description"

def test_delete_group(db_session, test_schema_group):
    group = create_group_in_db(db_session, test_schema_group.model_dump())
    assert delete_group_from_db(db_session, group.id) is True
    assert read_group_from_db(db_session, group.id) is None

def test_create_user_to_group_association(db_session, test_schema_group, test_schema_user):
    group = create_group_in_db(db_session, test_schema_group.model_dump())
    user = create_user_in_db(db_session, test_schema_user.model_dump())
    assert create_user_to_group_association_in_db(db_session, user.id, group.id) is True

def test_delete_user_to_group_association(db_session, test_schema_group, test_schema_user):
    group = create_group_in_db(db_session, test_schema_group.model_dump())
    user = create_user_in_db(db_session, test_schema_user.model_dump())
    create_user_to_group_association_in_db(db_session, user.id, group.id)
    assert delete_user_to_group_association_from_db(db_session, user.id, group.id) is True

def test_create_question_set_to_group_association(db_session, test_schema_group, test_schema_question_set):
    group = create_group_in_db(db_session, test_schema_group.model_dump())
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    assert create_question_set_to_group_association_in_db(db_session, question_set.id, group.id) is True

def test_delete_question_set_to_group_association(db_session, test_schema_group, test_schema_question_set):
    group = create_group_in_db(db_session, test_schema_group.model_dump())
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    create_question_set_to_group_association_in_db(db_session, question_set.id, group.id)
    assert delete_question_set_to_group_association_from_db(db_session, question_set.id, group.id) is True

def test_read_users_for_group(db_session, test_schema_group, test_schema_user):
    group = create_group_in_db(db_session, test_schema_group.model_dump())
    user = create_user_in_db(db_session, test_schema_user.model_dump())
    create_user_to_group_association_in_db(db_session, user.id, group.id)
    users = read_users_for_group_from_db(db_session, group.id)
    assert len(users) == 1
    assert users[0].id == user.id

def test_read_question_sets_for_group(db_session, test_schema_group, test_schema_question_set):
    group = create_group_in_db(db_session, test_schema_group.model_dump())
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    create_question_set_to_group_association_in_db(db_session, question_set.id, group.id)
    question_sets = read_question_sets_for_group_from_db(db_session, group.id)
    assert len(question_sets) == 1
    assert question_sets[0].id == question_set.id
