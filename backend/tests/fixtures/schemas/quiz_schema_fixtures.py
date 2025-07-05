# filename: backend/tests/fixtures/schemas/quiz_schema_fixtures.py

import pytest
import uuid

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
    unique_text = f"test_answer_{str(uuid.uuid4())[:8]}"
    return AnswerChoiceCreateSchema(
        text=unique_text,
        is_correct=True,
        explanation="This is a test explanation",
    )


@pytest.fixture(scope="function")
def test_schema_question(
    test_model_subject, test_model_topic, test_model_subtopic, test_model_concept
):
    """Create a test question creation schema."""
    unique_text = f"test_question_{str(uuid.uuid4())[:8]}"
    return QuestionCreateSchema(
        text=unique_text,
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
    unique_name = f"test_question_set_{str(uuid.uuid4())[:8]}"
    return QuestionSetCreateSchema(
        name=unique_name,
        description="This is a test question set",
        is_public=True,
        creator_id=test_model_user.id,
    )


@pytest.fixture(scope="function")
def test_schema_question_tag():
    """Create a test question tag creation schema."""
    unique_tag = f"test-tag-{str(uuid.uuid4())[:8]}"
    return QuestionTagCreateSchema(tag=unique_tag)