# filename: tests/models/test_concept_model.py

import pytest
from sqlalchemy.exc import IntegrityError
from app.models.concepts import ConceptModel
from app.models.subtopics import SubtopicModel

def test_concept_creation(db_session):
    concept = ConceptModel(name="Pythagorean Theorem")
    db_session.add(concept)
    db_session.commit()

    assert concept.id is not None
    assert concept.name == "Pythagorean Theorem"

def test_concept_subtopic_relationship(db_session):
    concept = ConceptModel(name="Binomial Theorem")
    subtopic = SubtopicModel(name="Algebraic Theorems")
    concept.subtopics.append(subtopic)
    db_session.add_all([concept, subtopic])
    db_session.commit()

    assert subtopic in concept.subtopics
    assert concept in subtopic.concepts

def test_concept_questions_relationship(db_session, test_model_questions):
    concept = ConceptModel(name="Logarithms")
    concept.questions.extend(test_model_questions[:2])
    db_session.add(concept)
    db_session.commit()

    assert len(concept.questions) == 2
    assert test_model_questions[0] in concept.questions
    assert test_model_questions[1] in concept.questions

def test_concept_required_fields(db_session):
    # Test missing name
    with pytest.raises(IntegrityError):
        concept = ConceptModel()
        db_session.add(concept)
        db_session.commit()
    db_session.rollback()

def test_concept_repr(db_session):
    concept = ConceptModel(name="Quadratic Formula")
    db_session.add(concept)
    db_session.commit()

    expected_repr = f"<Concept(id={concept.id}, name='Quadratic Formula')>"
    assert repr(concept) == expected_repr
