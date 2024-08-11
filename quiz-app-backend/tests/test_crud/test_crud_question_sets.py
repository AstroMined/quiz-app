# filename: tests/crud/test_crud_question_sets.py

import pytest
from app.crud.crud_question_sets import (
    create_question_set_in_db,
    read_question_set_from_db,
    read_question_sets_from_db,
    update_question_set_in_db,
    delete_question_set_from_db,
    create_question_set_to_question_association_in_db,
    delete_question_set_to_question_association_from_db,
    create_question_set_to_group_association_in_db,
    delete_question_set_to_group_association_from_db,
    read_questions_for_question_set_from_db,
    read_groups_for_question_set_from_db
)
from app.crud.crud_questions import create_question_in_db
from app.crud.crud_groups import create_group_in_db

def test_create_question_set(db_session, test_schema_question_set):
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    assert question_set.name == test_schema_question_set.name
    assert question_set.description == test_schema_question_set.description
    assert question_set.is_public == test_schema_question_set.is_public

def test_read_question_set(db_session, test_schema_question_set):
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    read_set = read_question_set_from_db(db_session, question_set.id)
    assert read_set.id == question_set.id
    assert read_set.name == question_set.name

def test_read_question_sets(db_session, test_schema_question_set):
    create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    question_sets = read_question_sets_from_db(db_session)
    assert len(question_sets) > 0

def test_update_question_set(db_session, test_schema_question_set):
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    updated_data = {"name": "Updated Question Set", "description": "Updated description"}
    updated_set = update_question_set_in_db(db_session, question_set.id, updated_data)
    assert updated_set.name == "Updated Question Set"
    assert updated_set.description == "Updated description"

def test_delete_question_set(db_session, test_schema_question_set):
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    assert delete_question_set_from_db(db_session, question_set.id) is True
    assert read_question_set_from_db(db_session, question_set.id) is None

def test_create_question_set_to_question_association(db_session, test_schema_question_set, test_schema_question):
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    assert create_question_set_to_question_association_in_db(db_session, question_set.id, question.id) is True

def test_delete_question_set_to_question_association(db_session, test_schema_question_set, test_schema_question):
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_set_to_question_association_in_db(db_session, question_set.id, question.id)
    assert delete_question_set_to_question_association_from_db(db_session, question_set.id, question.id) is True

def test_create_question_set_to_group_association(db_session, test_schema_question_set, test_schema_group):
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    group = create_group_in_db(db_session, test_schema_group.model_dump())
    assert create_question_set_to_group_association_in_db(db_session, question_set.id, group.id) is True

def test_delete_question_set_to_group_association(db_session, test_schema_question_set, test_schema_group):
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    group = create_group_in_db(db_session, test_schema_group.model_dump())
    create_question_set_to_group_association_in_db(db_session, question_set.id, group.id)
    assert delete_question_set_to_group_association_from_db(db_session, question_set.id, group.id) is True

def test_read_questions_for_question_set(db_session, test_schema_question_set, test_schema_question):
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_set_to_question_association_in_db(db_session, question_set.id, question.id)
    questions = read_questions_for_question_set_from_db(db_session, question_set.id)
    assert len(questions) == 1
    assert questions[0].id == question.id

def test_read_groups_for_question_set(db_session, test_schema_question_set, test_schema_group):
    question_set = create_question_set_in_db(db_session, test_schema_question_set.model_dump())
    group = create_group_in_db(db_session, test_schema_group.model_dump())
    create_question_set_to_group_association_in_db(db_session, question_set.id, group.id)
    groups = read_groups_for_question_set_from_db(db_session, question_set.id)
    assert len(groups) == 1
    assert groups[0].id == group.id
