# filename: tests/test_models/test_subject_model.py

import pytest
from sqlalchemy.exc import IntegrityError
from app.models.subjects import SubjectModel
from app.models.disciplines import DisciplineModel
from app.models.topics import TopicModel

def test_subject_creation(db_session):
    subject = SubjectModel(name="Mathematics")
    db_session.add(subject)
    db_session.commit()

    assert subject.id is not None
    assert subject.name == "Mathematics"

def test_subject_unique_name(db_session):
    subject1 = SubjectModel(name="Physics")
    db_session.add(subject1)
    db_session.commit()

    with pytest.raises(IntegrityError):
        subject2 = SubjectModel(name="Physics")
        db_session.add(subject2)
        db_session.commit()
    db_session.rollback()

def test_subject_discipline_relationship(db_session):
    subject = SubjectModel(name="Chemistry")
    discipline = DisciplineModel(name="Natural Sciences")
    subject.disciplines.append(discipline)
    db_session.add_all([subject, discipline])
    db_session.commit()

    assert discipline in subject.disciplines
    assert subject in discipline.subjects

def test_subject_topics_relationship(db_session):
    subject = SubjectModel(name="Biology")
    topic = TopicModel(name="Genetics")
    subject.topics.append(topic)
    db_session.add_all([subject, topic])
    db_session.commit()

    assert topic in subject.topics
    assert subject in topic.subjects

def test_subject_questions_relationship(db_session, test_model_questions):
    subject = SubjectModel(name="Geography")
    subject.questions.extend(test_model_questions[:2])
    db_session.add(subject)
    db_session.commit()

    assert len(subject.questions) == 2
    assert test_model_questions[0] in subject.questions
    assert test_model_questions[1] in subject.questions

def test_subject_required_fields(db_session):
    # Test missing name
    with pytest.raises(IntegrityError):
        subject = SubjectModel()
        db_session.add(subject)
        db_session.commit()
    db_session.rollback()

def test_subject_repr(db_session):
    subject = SubjectModel(name="History")
    db_session.add(subject)
    db_session.commit()

    expected_repr = f"<Subject(id={subject.id}, name='History')>"
    assert repr(subject) == expected_repr
