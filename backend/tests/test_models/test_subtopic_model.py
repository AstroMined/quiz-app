# filename: backend/tests/test_models/test_subtopic_model.py

import pytest
from sqlalchemy.exc import IntegrityError

from backend.app.models.concepts import ConceptModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.topics import TopicModel


def test_subtopic_creation(db_session):
    subtopic = SubtopicModel(name="Linear Equations")
    db_session.add(subtopic)
    db_session.commit()

    assert subtopic.id is not None
    assert subtopic.name == "Linear Equations"

def test_subtopic_topic_relationship(db_session):
    subtopic = SubtopicModel(name="Quadratic Equations")
    topic = TopicModel(name="Algebra")
    subtopic.topics.append(topic)
    db_session.add_all([subtopic, topic])
    db_session.commit()

    assert topic in subtopic.topics
    assert subtopic in topic.subtopics

def test_subtopic_concepts_relationship(db_session):
    subtopic = SubtopicModel(name="Trigonometric Functions")
    concept = ConceptModel(name="Sine Function")
    subtopic.concepts.append(concept)
    db_session.add_all([subtopic, concept])
    db_session.commit()

    assert concept in subtopic.concepts
    assert subtopic in concept.subtopics

def test_subtopic_questions_relationship(db_session, test_model_questions):
    subtopic = SubtopicModel(name="Limits")
    subtopic.questions.extend(test_model_questions[:2])
    db_session.add(subtopic)
    db_session.commit()

    assert len(subtopic.questions) == 2
    assert test_model_questions[0] in subtopic.questions
    assert test_model_questions[1] in subtopic.questions

def test_subtopic_required_fields(db_session):
    # Test missing name
    with pytest.raises(IntegrityError):
        subtopic = SubtopicModel()
        db_session.add(subtopic)
        db_session.commit()
    db_session.rollback()

def test_subtopic_repr(db_session):
    subtopic = SubtopicModel(name="Derivatives")
    db_session.add(subtopic)
    db_session.commit()

    expected_repr = f"<Subtopic(id={subtopic.id}, name='Derivatives')>"
    assert repr(subtopic) == expected_repr
