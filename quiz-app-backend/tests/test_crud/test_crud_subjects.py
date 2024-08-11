# filename: tests/crud/test_crud_subjects.py

import pytest
from app.crud.crud_subjects import (
    create_subject_in_db,
    read_subject_from_db,
    read_subject_by_name_from_db,
    read_subjects_from_db,
    update_subject_in_db,
    delete_subject_from_db,
    create_discipline_to_subject_association_in_db,
    delete_discipline_to_subject_association_from_db,
    create_subject_to_topic_association_in_db,
    delete_subject_to_topic_association_from_db,
    create_question_to_subject_association_in_db,
    delete_question_to_subject_association_from_db,
    read_disciplines_for_subject_from_db,
    read_topics_for_subject_from_db,
    read_questions_for_subject_from_db
)
from app.crud.crud_disciplines import create_discipline_in_db
from app.crud.crud_topics import create_topic_in_db
from app.crud.crud_questions import create_question_in_db

def test_create_subject(db_session, test_schema_subject):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    assert subject.name == test_schema_subject.name

def test_read_subject(db_session, test_schema_subject):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    read_subject = read_subject_from_db(db_session, subject.id)
    assert read_subject.id == subject.id
    assert read_subject.name == subject.name

def test_read_subject_by_name(db_session, test_schema_subject):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    read_subject = read_subject_by_name_from_db(db_session, subject.name)
    assert read_subject.id == subject.id
    assert read_subject.name == subject.name

def test_read_subjects(db_session, test_schema_subject):
    create_subject_in_db(db_session, test_schema_subject.model_dump())
    subjects = read_subjects_from_db(db_session)
    assert len(subjects) > 0

def test_update_subject(db_session, test_schema_subject):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    updated_data = {"name": "Updated Subject"}
    updated_subject = update_subject_in_db(db_session, subject.id, updated_data)
    assert updated_subject.name == "Updated Subject"

def test_delete_subject(db_session, test_schema_subject):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    assert delete_subject_from_db(db_session, subject.id) is True
    assert read_subject_from_db(db_session, subject.id) is None

def test_create_discipline_to_subject_association(db_session, test_schema_subject, test_schema_discipline):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    assert create_discipline_to_subject_association_in_db(db_session, discipline.id, subject.id) is True

def test_delete_discipline_to_subject_association(db_session, test_schema_subject, test_schema_discipline):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    create_discipline_to_subject_association_in_db(db_session, discipline.id, subject.id)
    assert delete_discipline_to_subject_association_from_db(db_session, discipline.id, subject.id) is True

def test_create_subject_to_topic_association(db_session, test_schema_subject, test_schema_topic):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    assert create_subject_to_topic_association_in_db(db_session, subject.id, topic.id) is True

def test_delete_subject_to_topic_association(db_session, test_schema_subject, test_schema_topic):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    create_subject_to_topic_association_in_db(db_session, subject.id, topic.id)
    assert delete_subject_to_topic_association_from_db(db_session, subject.id, topic.id) is True

def test_create_question_to_subject_association(db_session, test_schema_subject, test_schema_question):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    assert create_question_to_subject_association_in_db(db_session, question.id, subject.id) is True

def test_delete_question_to_subject_association(db_session, test_schema_subject, test_schema_question):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_subject_association_in_db(db_session, question.id, subject.id)
    assert delete_question_to_subject_association_from_db(db_session, question.id, subject.id) is True

def test_read_disciplines_for_subject(db_session, test_schema_subject, test_schema_discipline):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    discipline = create_discipline_in_db(db_session, test_schema_discipline.model_dump())
    create_discipline_to_subject_association_in_db(db_session, discipline.id, subject.id)
    disciplines = read_disciplines_for_subject_from_db(db_session, subject.id)
    assert len(disciplines) == 1
    assert disciplines[0].id == discipline.id

def test_read_topics_for_subject(db_session, test_schema_subject, test_schema_topic):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    create_subject_to_topic_association_in_db(db_session, subject.id, topic.id)
    topics = read_topics_for_subject_from_db(db_session, subject.id)
    assert len(topics) == 1
    assert topics[0].id == topic.id

def test_read_questions_for_subject(db_session, test_schema_subject, test_schema_question):
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_subject_association_in_db(db_session, question.id, subject.id)
    questions = read_questions_for_subject_from_db(db_session, subject.id)
    assert len(questions) == 1
    assert questions[0].id == question.id
