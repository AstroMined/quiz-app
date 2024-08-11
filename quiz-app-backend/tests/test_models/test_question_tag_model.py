# filename: tests/models/test_question_tag_model.py

import pytest
from sqlalchemy.exc import IntegrityError
from app.models.question_tags import QuestionTagModel

def test_question_tag_creation(db_session):
    tag = QuestionTagModel(tag="geography")
    db_session.add(tag)
    db_session.commit()

    assert tag.id is not None
    assert tag.tag == "geography"

def test_question_tag_unique_constraint(db_session):
    tag1 = QuestionTagModel(tag="history")
    db_session.add(tag1)
    db_session.commit()

    # Try to create another tag with the same name
    with pytest.raises(IntegrityError):
        tag2 = QuestionTagModel(tag="history")
        db_session.add(tag2)
        db_session.commit()
    
    db_session.rollback()

def test_question_tag_question_relationship(db_session, test_model_questions):
    tag = QuestionTagModel(tag="science")
    tag.questions.append(test_model_questions[0])
    db_session.add(tag)
    db_session.commit()

    assert test_model_questions[0] in tag.questions
    assert tag in test_model_questions[0].question_tags

def test_question_tag_multiple_questions(db_session, test_model_questions):
    tag = QuestionTagModel(tag="math")
    tag.questions.extend(test_model_questions[:2])  # Add the tag to the first two questions
    db_session.add(tag)
    db_session.commit()

    assert len(tag.questions) == 2
    assert test_model_questions[0] in tag.questions
    assert test_model_questions[1] in tag.questions

def test_question_tag_required_fields(db_session):
    # Test missing tag
    with pytest.raises(IntegrityError):
        tag = QuestionTagModel()
        db_session.add(tag)
        db_session.commit()
    db_session.rollback()

def test_question_tag_repr(db_session):
    tag = QuestionTagModel(tag="biology")
    db_session.add(tag)
    db_session.commit()

    expected_repr = f"<QuestionTagModel(id={tag.id}, tag='biology')>"
    assert repr(tag) == expected_repr
