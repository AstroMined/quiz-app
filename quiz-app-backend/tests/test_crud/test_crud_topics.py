# filename: tests/crud/test_crud_topics.py

import pytest
from app.crud.crud_topics import (
    create_topic_in_db,
    read_topic_from_db,
    read_topic_by_name_from_db,
    read_topics_from_db,
    update_topic_in_db,
    delete_topic_from_db,
    create_subject_to_topic_association_in_db,
    delete_subject_to_topic_association_from_db,
    create_topic_to_subtopic_association_in_db,
    delete_topic_to_subtopic_association_from_db,
    create_question_to_topic_association_in_db,
    delete_question_to_topic_association_from_db,
    read_subjects_for_topic_from_db,
    read_subtopics_for_topic_from_db,
    read_questions_for_topic_from_db
)
from app.crud.crud_subjects import create_subject_in_db
from app.crud.crud_subtopics import create_subtopic_in_db
from app.crud.crud_questions import create_question_in_db

def test_create_topic(db_session, test_schema_topic):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    assert topic.name == test_schema_topic.name

def test_read_topic(db_session, test_schema_topic):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    read_topic = read_topic_from_db(db_session, topic.id)
    assert read_topic.id == topic.id
    assert read_topic.name == topic.name

def test_read_topic_by_name(db_session, test_schema_topic):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    read_topic = read_topic_by_name_from_db(db_session, topic.name)
    assert read_topic.id == topic.id
    assert read_topic.name == topic.name

def test_read_topics(db_session, test_schema_topic):
    create_topic_in_db(db_session, test_schema_topic.model_dump())
    topics = read_topics_from_db(db_session)
    assert len(topics) > 0

def test_update_topic(db_session, test_schema_topic):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    updated_data = {"name": "Updated Topic"}
    updated_topic = update_topic_in_db(db_session, topic.id, updated_data)
    assert updated_topic.name == "Updated Topic"

def test_delete_topic(db_session, test_schema_topic):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    assert delete_topic_from_db(db_session, topic.id) is True
    assert read_topic_from_db(db_session, topic.id) is None

def test_create_subject_to_topic_association(db_session, test_schema_topic, test_schema_subject):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    assert create_subject_to_topic_association_in_db(db_session, subject.id, topic.id) is True

def test_delete_subject_to_topic_association(db_session, test_schema_topic, test_schema_subject):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    create_subject_to_topic_association_in_db(db_session, subject.id, topic.id)
    assert delete_subject_to_topic_association_from_db(db_session, subject.id, topic.id) is True

def test_create_topic_to_subtopic_association(db_session, test_schema_topic, test_schema_subtopic):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    assert create_topic_to_subtopic_association_in_db(db_session, topic.id, subtopic.id) is True

def test_delete_topic_to_subtopic_association(db_session, test_schema_topic, test_schema_subtopic):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    create_topic_to_subtopic_association_in_db(db_session, topic.id, subtopic.id)
    assert delete_topic_to_subtopic_association_from_db(db_session, topic.id, subtopic.id) is True

def test_create_question_to_topic_association(db_session, test_schema_topic, test_schema_question):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    assert create_question_to_topic_association_in_db(db_session, question.id, topic.id) is True

def test_delete_question_to_topic_association(db_session, test_schema_topic, test_schema_question):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_topic_association_in_db(db_session, question.id, topic.id)
    assert delete_question_to_topic_association_from_db(db_session, question.id, topic.id) is True

def test_read_subjects_for_topic(db_session, test_schema_topic, test_schema_subject):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    subject = create_subject_in_db(db_session, test_schema_subject.model_dump())
    create_subject_to_topic_association_in_db(db_session, subject.id, topic.id)
    subjects = read_subjects_for_topic_from_db(db_session, topic.id)
    assert len(subjects) == 1
    assert subjects[0].id == subject.id

def test_read_subtopics_for_topic(db_session, test_schema_topic, test_schema_subtopic):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    create_topic_to_subtopic_association_in_db(db_session, topic.id, subtopic.id)
    subtopics = read_subtopics_for_topic_from_db(db_session, topic.id)
    assert len(subtopics) == 1
    assert subtopics[0].id == subtopic.id

def test_read_questions_for_topic(db_session, test_schema_topic, test_schema_question):
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_topic_association_in_db(db_session, question.id, topic.id)
    questions = read_questions_for_topic_from_db(db_session, topic.id)
    assert len(questions) == 1
    assert questions[0].id == question.id
    