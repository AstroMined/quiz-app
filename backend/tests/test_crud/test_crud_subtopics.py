# filename: backend/tests/crud/test_crud_subtopics.py

import pytest

from backend.app.crud.crud_concepts import create_concept_in_db
from backend.app.crud.crud_questions import create_question_in_db
from backend.app.crud.crud_subtopics import (
    create_question_to_subtopic_association_in_db, create_subtopic_in_db,
    create_subtopic_to_concept_association_in_db,
    create_topic_to_subtopic_association_in_db,
    delete_question_to_subtopic_association_from_db, delete_subtopic_from_db,
    delete_subtopic_to_concept_association_from_db,
    delete_topic_to_subtopic_association_from_db,
    read_concepts_for_subtopic_from_db, read_questions_for_subtopic_from_db,
    read_subtopic_by_name_from_db, read_subtopic_from_db,
    read_subtopics_from_db, read_topics_for_subtopic_from_db,
    update_subtopic_in_db)
from backend.app.crud.crud_topics import create_topic_in_db


def test_create_subtopic(db_session, test_schema_subtopic):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    assert subtopic.name == test_schema_subtopic.name

def test_read_subtopic(db_session, test_schema_subtopic):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    read_subtopic = read_subtopic_from_db(db_session, subtopic.id)
    assert read_subtopic.id == subtopic.id
    assert read_subtopic.name == subtopic.name

def test_read_subtopic_by_name(db_session, test_schema_subtopic):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    read_subtopic = read_subtopic_by_name_from_db(db_session, subtopic.name)
    assert read_subtopic.id == subtopic.id
    assert read_subtopic.name == subtopic.name

def test_read_subtopics(db_session, test_schema_subtopic):
    create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    subtopics = read_subtopics_from_db(db_session)
    assert len(subtopics) > 0

def test_update_subtopic(db_session, test_schema_subtopic):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    updated_data = {"name": "Updated Subtopic"}
    updated_subtopic = update_subtopic_in_db(db_session, subtopic.id, updated_data)
    assert updated_subtopic.name == "Updated Subtopic"

def test_delete_subtopic(db_session, test_schema_subtopic):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    assert delete_subtopic_from_db(db_session, subtopic.id) is True
    assert read_subtopic_from_db(db_session, subtopic.id) is None

def test_create_topic_to_subtopic_association(db_session, test_schema_subtopic, test_schema_topic):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    assert create_topic_to_subtopic_association_in_db(db_session, topic.id, subtopic.id) is True

def test_delete_topic_to_subtopic_association(db_session, test_schema_subtopic, test_schema_topic):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    create_topic_to_subtopic_association_in_db(db_session, topic.id, subtopic.id)
    assert delete_topic_to_subtopic_association_from_db(db_session, topic.id, subtopic.id) is True

def test_create_subtopic_to_concept_association(db_session, test_schema_subtopic, test_schema_concept):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    assert create_subtopic_to_concept_association_in_db(db_session, subtopic.id, concept.id) is True

def test_delete_subtopic_to_concept_association(db_session, test_schema_subtopic, test_schema_concept):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    create_subtopic_to_concept_association_in_db(db_session, subtopic.id, concept.id)
    assert delete_subtopic_to_concept_association_from_db(db_session, subtopic.id, concept.id) is True

def test_create_question_to_subtopic_association(db_session, test_schema_subtopic, test_schema_question):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    assert create_question_to_subtopic_association_in_db(db_session, question.id, subtopic.id) is True

def test_delete_question_to_subtopic_association(db_session, test_schema_subtopic, test_schema_question):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_subtopic_association_in_db(db_session, question.id, subtopic.id)
    assert delete_question_to_subtopic_association_from_db(db_session, question.id, subtopic.id) is True

def test_read_topics_for_subtopic(db_session, test_schema_subtopic, test_schema_topic):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    topic = create_topic_in_db(db_session, test_schema_topic.model_dump())
    create_topic_to_subtopic_association_in_db(db_session, topic.id, subtopic.id)
    topics = read_topics_for_subtopic_from_db(db_session, subtopic.id)
    assert len(topics) == 1
    assert topics[0].id == topic.id

def test_read_concepts_for_subtopic(db_session, test_schema_subtopic, test_schema_concept):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    concept = create_concept_in_db(db_session, test_schema_concept.model_dump())
    create_subtopic_to_concept_association_in_db(db_session, subtopic.id, concept.id)
    concepts = read_concepts_for_subtopic_from_db(db_session, subtopic.id)
    assert len(concepts) == 1
    assert concepts[0].id == concept.id

def test_read_questions_for_subtopic(db_session, test_schema_subtopic, test_schema_question):
    subtopic = create_subtopic_in_db(db_session, test_schema_subtopic.model_dump())
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    create_question_to_subtopic_association_in_db(db_session, question.id, subtopic.id)
    questions = read_questions_for_subtopic_from_db(db_session, subtopic.id)
    assert len(questions) == 1
    assert questions[0].id == question.id
