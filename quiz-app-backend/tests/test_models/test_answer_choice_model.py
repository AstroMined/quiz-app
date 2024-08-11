# filename: tests/models/test_answer_choice_model.py

import pytest
from sqlalchemy.exc import IntegrityError
from app.models.answer_choices import AnswerChoiceModel
from app.models.questions import QuestionModel
from app.models.user_responses import UserResponseModel

def test_answer_choice_creation(db_session):
    answer_choice = AnswerChoiceModel(
        text="Paris",
        is_correct=True,
        explanation="Paris is the capital of France"
    )
    db_session.add(answer_choice)
    db_session.commit()

    assert answer_choice.id is not None
    assert answer_choice.text == "Paris"
    assert answer_choice.is_correct is True
    assert answer_choice.explanation == "Paris is the capital of France"

def test_answer_choice_question_relationship(db_session, test_model_questions):
    answer_choice = AnswerChoiceModel(
        text="Paris",
        is_correct=True,
        explanation="Paris is the capital of France"
    )
    answer_choice.questions.append(test_model_questions[0])
    db_session.add(answer_choice)
    db_session.commit()

    assert test_model_questions[0] in answer_choice.questions
    assert answer_choice in test_model_questions[0].answer_choices

def test_answer_choice_multiple_questions(db_session, test_model_questions):
    answer_choice = AnswerChoiceModel(
        text="Paris",
        is_correct=True,
        explanation="Paris is the capital of France"
    )
    
    answer_choice.questions.extend(test_model_questions[:2])  # Use the first two questions from the fixture
    db_session.add(answer_choice)
    db_session.commit()

    assert len(answer_choice.questions) == 2
    assert test_model_questions[0] in answer_choice.questions
    assert test_model_questions[1] in answer_choice.questions

def test_answer_choice_user_response_relationship(db_session, test_model_questions, test_model_user):
    answer_choice = AnswerChoiceModel(
        text="Paris",
        is_correct=True,
        explanation="Paris is the capital of France"
    )
    answer_choice.questions.append(test_model_questions[0])
    db_session.add(answer_choice)
    db_session.commit()

    user_response = UserResponseModel(
        user_id=test_model_user.id,
        question_id=test_model_questions[0].id,
        answer_choice_id=answer_choice.id,
        is_correct=True
    )
    db_session.add(user_response)
    db_session.commit()

    assert user_response in answer_choice.user_responses
    assert user_response.answer_choice == answer_choice

def test_answer_choice_required_fields(db_session):
    # Test missing text
    with pytest.raises(IntegrityError):
        answer_choice = AnswerChoiceModel(
            is_correct=True
        )
        db_session.add(answer_choice)
        db_session.commit()
    db_session.rollback()

    # Test missing is_correct
    with pytest.raises(IntegrityError):
        answer_choice = AnswerChoiceModel(
            text="Paris"
        )
        db_session.add(answer_choice)
        db_session.commit()
    db_session.rollback()

def test_answer_choice_repr(db_session):
    answer_choice = AnswerChoiceModel(
        text="Paris",
        is_correct=True,
        explanation="Paris is the capital of France"
    )
    db_session.add(answer_choice)
    db_session.commit()

    expected_repr = f"<AnswerChoiceModel(id={answer_choice.id}, text='Paris...', is_correct=True)>"
    assert repr(answer_choice) == expected_repr
