# filename: backend/tests/models/test_question_set_model.py

import pytest
from sqlalchemy.exc import IntegrityError

from backend.app.models.question_sets import QuestionSetModel


def test_question_set_creation(db_session, test_model_user):
    question_set = QuestionSetModel(
        name="Geography Quiz",
        is_public=True,
        creator_id=test_model_user.id
    )
    db_session.add(question_set)
    db_session.commit()

    assert question_set.id is not None
    assert question_set.name == "Geography Quiz"
    assert question_set.is_public is True
    assert question_set.creator_id == test_model_user.id

def test_question_set_creator_relationship(db_session, test_model_user):
    question_set = QuestionSetModel(
        name="History Quiz",
        is_public=False,
        creator_id=test_model_user.id
    )
    db_session.add(question_set)
    db_session.commit()

    assert question_set.creator == test_model_user
    assert question_set in test_model_user.created_question_sets

def test_question_set_questions_relationship(db_session, test_model_user, test_model_questions):
    question_set = QuestionSetModel(
        name="Science Quiz",
        is_public=True,
        creator_id=test_model_user.id
    )
    question_set.questions.extend(test_model_questions[:2])
    db_session.add(question_set)
    db_session.commit()

    assert len(question_set.questions) == 2
    assert test_model_questions[0] in question_set.questions
    assert test_model_questions[1] in question_set.questions

def test_question_set_groups_relationship(db_session, test_model_user, test_model_group):
    question_set = QuestionSetModel(
        name="Math Quiz",
        is_public=True,
        creator_id=test_model_user.id
    )
    question_set.groups.append(test_model_group)
    db_session.add(question_set)
    db_session.commit()

    assert test_model_group in question_set.groups
    assert question_set in test_model_group.question_sets

def test_question_set_required_fields(db_session, test_model_user):
    # Test missing name
    with pytest.raises(IntegrityError):
        question_set = QuestionSetModel(
            is_public=True,
            creator_id=test_model_user.id
        )
        db_session.add(question_set)
        db_session.commit()
    db_session.rollback()

def test_question_set_repr(db_session, test_model_user):
    question_set = QuestionSetModel(
        name="Biology Quiz",
        is_public=True,
        creator_id=test_model_user.id
    )
    db_session.add(question_set)
    db_session.commit()

    expected_repr = f"<QuestionSetModel(id={question_set.id}, name='Biology Quiz', is_public=True, creator_id={test_model_user.id})>"
    assert repr(question_set) == expected_repr
