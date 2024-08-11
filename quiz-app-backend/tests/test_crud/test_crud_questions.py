# filename: tests/crud/test_crud_questions.py

import pytest
from app.crud.crud_questions import (
    create_question_in_db,
    read_question_from_db,
    read_questions_from_db,
    update_question_in_db,
    delete_question_from_db
)
from app.models.questions import DifficultyLevel

def test_create_question(db_session, test_schema_question):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    assert question.text == test_schema_question.text
    assert question.difficulty == test_schema_question.difficulty

def test_create_question_with_answers(db_session, test_schema_question_with_answers):
    question = create_question_in_db(db_session, test_schema_question_with_answers.model_dump())
    assert question.text == test_schema_question_with_answers.text
    assert question.difficulty == test_schema_question_with_answers.difficulty
    assert len(question.answer_choices) == len(test_schema_question_with_answers.answer_choices)

def test_read_question(db_session, test_schema_question):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    read_question = read_question_from_db(db_session, question.id)
    assert read_question.id == question.id
    assert read_question.text == question.text

def test_read_questions(db_session, test_schema_question):
    create_question_in_db(db_session, test_schema_question.model_dump())
    questions = read_questions_from_db(db_session)
    assert len(questions) > 0

def test_update_question(db_session, test_schema_question):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    updated_data = {"text": "Updated question text", "difficulty": DifficultyLevel.HARD}
    updated_question = update_question_in_db(db_session, question.id, updated_data)
    assert updated_question.text == "Updated question text"
    assert updated_question.difficulty == DifficultyLevel.HARD

def test_delete_question(db_session, test_schema_question):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    assert delete_question_from_db(db_session, question.id) is True
    assert read_question_from_db(db_session, question.id) is None

def test_create_question_with_associations(db_session, test_schema_question, test_model_subject, test_model_topic, test_model_subtopic, test_model_concept):
    question_data = test_schema_question.model_dump()
    question_data.update({
        "subject_ids": [test_model_subject.id],
        "topic_ids": [test_model_topic.id],
        "subtopic_ids": [test_model_subtopic.id],
        "concept_ids": [test_model_concept.id]
    })
    question = create_question_in_db(db_session, question_data)
    assert len(question.subjects) == 1
    assert len(question.topics) == 1
    assert len(question.subtopics) == 1
    assert len(question.concepts) == 1

def test_update_question_associations(db_session, test_schema_question, test_model_subject, test_model_topic, test_model_subtopic, test_model_concept):
    question = create_question_in_db(db_session, test_schema_question.model_dump())
    updated_data = {
        "subject_ids": [test_model_subject.id],
        "topic_ids": [test_model_topic.id],
        "subtopic_ids": [test_model_subtopic.id],
        "concept_ids": [test_model_concept.id]
    }
    updated_question = update_question_in_db(db_session, question.id, updated_data)
    assert len(updated_question.subjects) == 1
    assert len(updated_question.topics) == 1
    assert len(updated_question.subtopics) == 1
    assert len(updated_question.concepts) == 1
