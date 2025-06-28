# filename: backend/tests/fixtures/schemas/quiz_schema_fixtures.py

import pytest

from backend.app.schemas.questions import (
    QuestionCreateSchema,
    QuestionWithAnswersCreateSchema,
)
from backend.app.schemas.answer_choices import AnswerChoiceCreateSchema
from backend.app.schemas.question_sets import QuestionSetCreateSchema
from backend.app.schemas.question_tags import QuestionTagCreateSchema


@pytest.fixture(scope="function")
def test_schema_answer_choice():
    """Create a test answer choice creation schema."""
    return AnswerChoiceCreateSchema(
        text="test_schema answer choice",
        is_correct=True,
        explanation="This is a test explanation",
    )


@pytest.fixture(scope="function")
def test_schema_question(
    test_model_subject, test_model_topic, test_model_subtopic, test_model_concept
):
    """Create a test question creation schema."""
    return QuestionCreateSchema(
        text="test_schema question",
        difficulty="Medium",
        subject_ids=[test_model_subject.id],
        topic_ids=[test_model_topic.id],
        subtopic_ids=[test_model_subtopic.id],
        concept_ids=[test_model_concept.id],
    )


@pytest.fixture(scope="function")
def test_schema_question_with_answers(test_schema_question, test_schema_answer_choice):
    """Create a test question with answers creation schema."""
    question_with_answers = test_schema_question.model_dump()
    question_with_answers["answer_choices"] = [test_schema_answer_choice]
    return QuestionWithAnswersCreateSchema(**question_with_answers)


@pytest.fixture(scope="function")
def test_schema_question_set(test_model_user):
    """Create a test question set creation schema."""
    return QuestionSetCreateSchema(
        name="test_schema Question Set",
        description="This is a test question set",
        is_public=True,
        creator_id=test_model_user.id,
    )


@pytest.fixture(scope="function")
def test_schema_question_tag():
    """Create a test question tag creation schema."""
    return QuestionTagCreateSchema(tag="test-tag")