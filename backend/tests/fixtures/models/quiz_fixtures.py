# filename: backend/tests/fixtures/models/quiz_fixtures.py

import pytest

from backend.app.models.questions import QuestionModel
from backend.app.models.answer_choices import AnswerChoiceModel
from backend.app.models.question_sets import QuestionSetModel
from backend.app.models.question_tags import QuestionTagModel


@pytest.fixture(scope="function")
def test_model_tag(db_session):
    """Create a test question tag."""
    tag = QuestionTagModel(tag="Test Tag")
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)
    return tag


@pytest.fixture(scope="function")
def test_model_question_set(db_session, test_model_user_with_group):
    """Create a test question set."""
    question_set = QuestionSetModel(
        name="Test Question Set",
        is_public=True,
        creator_id=test_model_user_with_group.id,
    )
    db_session.add(question_set)
    db_session.commit()
    db_session.refresh(question_set)
    return question_set


@pytest.fixture(scope="function")
def test_model_answer_choices(db_session):
    """Create test answer choices for questions."""
    answer_choices = [
        AnswerChoiceModel(
            text="Answer 1 for Q1", is_correct=True, explanation="Explanation 1 for Q1"
        ),
        AnswerChoiceModel(
            text="Answer 2 for Q1", is_correct=False, explanation="Explanation 2 for Q1"
        ),
        AnswerChoiceModel(
            text="Answer 1 for Q2", is_correct=True, explanation="Explanation 1 for Q2"
        ),
        AnswerChoiceModel(
            text="Answer 2 for Q2", is_correct=False, explanation="Explanation 2 for Q2"
        ),
    ]

    for answer_choice in answer_choices:
        db_session.add(answer_choice)
    db_session.commit()
    return answer_choices


@pytest.fixture(scope="function")
def test_model_questions(
    db_session,
    test_model_subject,
    test_model_topic,
    test_model_subtopic,
    test_model_concept,
    test_model_answer_choices,
):
    """Create test questions with associated content and answer choices."""
    questions = []
    for i in range(2):
        question = QuestionModel(
            text=f"Test Question {i+1}",
            difficulty="EASY",
            subjects=[test_model_subject],
            topics=[test_model_topic],
            subtopics=[test_model_subtopic],
            concepts=[test_model_concept],
        )
        db_session.add(question)
        db_session.flush()  # Flush to get the question ID

        # Associate answer choices with the question
        question.answer_choices.extend(test_model_answer_choices[i * 2 : (i + 1) * 2])
        questions.append(question)

    db_session.commit()
    return questions