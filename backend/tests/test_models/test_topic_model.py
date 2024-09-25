# filename: backend/tests/test_models/test_topic_model.py

import pytest
from sqlalchemy.exc import IntegrityError

from backend.app.models.subjects import SubjectModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.topics import TopicModel


def test_topic_creation(db_session):
    topic = TopicModel(name="Algebra")
    db_session.add(topic)
    db_session.commit()

    assert topic.id is not None
    assert topic.name == "Algebra"


def test_topic_subject_relationship(db_session):
    topic = TopicModel(name="Geometry")
    subject = SubjectModel(name="Mathematics")
    topic.subjects.append(subject)
    db_session.add_all([topic, subject])
    db_session.commit()

    assert subject in topic.subjects
    assert topic in subject.topics


def test_topic_subtopics_relationship(db_session):
    topic = TopicModel(name="Calculus")
    subtopic = SubtopicModel(name="Derivatives")
    topic.subtopics.append(subtopic)
    db_session.add_all([topic, subtopic])
    db_session.commit()

    assert subtopic in topic.subtopics
    assert topic in subtopic.topics


def test_topic_questions_relationship(db_session, test_model_questions):
    topic = TopicModel(name="Statistics")
    topic.questions.extend(test_model_questions[:2])
    db_session.add(topic)
    db_session.commit()

    assert len(topic.questions) == 2
    assert test_model_questions[0] in topic.questions
    assert test_model_questions[1] in topic.questions


def test_topic_required_fields(db_session):
    # Test missing name
    with pytest.raises(IntegrityError):
        topic = TopicModel()
        db_session.add(topic)
        db_session.commit()
    db_session.rollback()


def test_topic_repr(db_session):
    topic = TopicModel(name="Trigonometry")
    db_session.add(topic)
    db_session.commit()

    expected_repr = f"<Topic(id={topic.id}, name='Trigonometry')>"
    assert repr(topic) == expected_repr
