# filename: backend/tests/crud/test_crud_question_tags.py

from backend.app.crud.crud_question_tags import (
    create_question_tag_in_db, create_question_to_tag_association_in_db,
    delete_question_tag_from_db, delete_question_to_tag_association_from_db,
    read_question_tag_by_tag_from_db, read_question_tag_from_db,
    read_question_tags_from_db, read_questions_for_tag_from_db,
    read_tags_for_question_from_db, update_question_tag_in_db)
from backend.app.crud.crud_questions import create_question_in_db


def test_create_question_tag(db_session, test_schema_question_tag):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    assert tag.tag == test_schema_question_tag.tag

def test_read_question_tag(db_session, test_schema_question_tag):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    read_tag = read_question_tag_from_db(db_session, tag.id)
    assert read_tag.id == tag.id
    assert read_tag.tag == tag.tag

def test_read_question_tag_by_tag(db_session, test_schema_question_tag):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    read_tag = read_question_tag_by_tag_from_db(db_session, tag.tag)
    assert read_tag.id == tag.id
    assert read_tag.tag == tag.tag

def test_read_question_tags(db_session, test_schema_question_tag):
    create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    tags = read_question_tags_from_db(db_session)
    assert len(tags) > 0

def test_update_question_tag(db_session, test_schema_question_tag):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    updated_data = {"tag": "updated-tag"}
    updated_tag = update_question_tag_in_db(db_session, tag.id, updated_data)
    assert updated_tag.tag == "updated-tag"

def test_delete_question_tag(db_session, test_schema_question_tag):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    assert delete_question_tag_from_db(db_session, tag.id) is True
    assert read_question_tag_from_db(db_session, tag.id) is None

def test_create_question_to_tag_association(db_session, test_schema_question_tag, test_schema_question):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    assert create_question_to_tag_association_in_db(db_session, question.id, tag.id) is True

def test_delete_question_to_tag_association(db_session, test_schema_question_tag, test_schema_question):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_tag_association_in_db(db_session, question.id, tag.id)
    assert delete_question_to_tag_association_from_db(db_session, question.id, tag.id) is True

def test_read_tags_for_question(db_session, test_schema_question_tag, test_schema_question):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_tag_association_in_db(db_session, question.id, tag.id)
    tags = read_tags_for_question_from_db(db_session, question.id)
    assert len(tags) == 1
    assert tags[0].id == tag.id

def test_read_questions_for_tag(db_session, test_schema_question_tag, test_schema_question):
    tag = create_question_tag_in_db(db_session, test_schema_question_tag.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_tag_association_in_db(db_session, question.id, tag.id)
    questions = read_questions_for_tag_from_db(db_session, tag.id)
    assert len(questions) == 1
    assert questions[0].id == question.id
