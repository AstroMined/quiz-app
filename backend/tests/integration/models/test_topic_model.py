# filename: backend/tests/test_models/test_topic_model.py

import pytest
from sqlalchemy.exc import IntegrityError

from backend.app.models.subjects import SubjectModel
from backend.app.models.subtopics import SubtopicModel
from backend.app.models.topics import TopicModel


def test_topic_creation(db_session):
    import uuid
    unique_name = f"Algebra_{str(uuid.uuid4())[:8]}"
    topic = TopicModel(name=unique_name)
    db_session.add(topic)
    db_session.commit()

    assert topic.id is not None
    assert topic.name == unique_name


def test_topic_subject_relationship(db_session):
    import uuid
    unique_topic_name = f"Geometry_{str(uuid.uuid4())[:8]}"
    unique_subject_name = f"Mathematics_{str(uuid.uuid4())[:8]}"
    topic = TopicModel(name=unique_topic_name)
    subject = SubjectModel(name=unique_subject_name)
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


def test_topic_schema_from_attributes(db_session, test_model_topic):
    from backend.app.schemas.topics import TopicSchema
    
    schema = TopicSchema.model_validate(test_model_topic)
    assert schema.id == test_model_topic.id
    assert schema.name == test_model_topic.name
    assert isinstance(schema.subjects, list)
    assert isinstance(schema.subtopics, list)
    assert isinstance(schema.questions, list)
    for subject in schema.subjects:
        assert "id" in subject
        assert "name" in subject
    for subtopic in schema.subtopics:
        assert "id" in subtopic
        assert "name" in subtopic
    for question in schema.questions:
        assert "id" in question
        assert "name" in question
