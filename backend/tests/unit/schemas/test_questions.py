# filename: backend/tests/test_schemas_questions.py

import pytest
from pydantic import ValidationError

from backend.app.schemas.answer_choices import AnswerChoiceSchema
from backend.app.schemas.questions import (
    DetailedQuestionSchema,
    DifficultyLevel,
    QuestionBaseSchema,
    QuestionCreateSchema,
    QuestionReplaceSchema,
    QuestionUpdateSchema,
    QuestionWithAnswersCreateSchema,
    QuestionWithAnswersReplaceSchema,
)


def test_question_create_schema(
    test_model_subject, test_model_topic, test_model_subtopic, test_model_concept
):
    question_data = {
        "text": "What is the capital of France?",
        "difficulty": DifficultyLevel.EASY,
        "subject_ids": [test_model_subject.id],
        "topic_ids": [test_model_topic.id],
        "subtopic_ids": [test_model_subtopic.id],
        "concept_ids": [test_model_concept.id],
    }
    question_schema = QuestionCreateSchema(**question_data)
    assert question_schema.text == "What is the capital of France?"
    assert question_schema.difficulty == DifficultyLevel.EASY
    assert question_schema.subject_ids == [test_model_subject.id]
    assert question_schema.topic_ids == [test_model_topic.id]
    assert question_schema.subtopic_ids == [test_model_subtopic.id]
    assert question_schema.concept_ids == [test_model_concept.id]


def test_question_create_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        QuestionCreateSchema(text="", difficulty=DifficultyLevel.EASY)
    assert "String should have at least 1 character" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        QuestionCreateSchema(text="Valid question", difficulty="Invalid")
    assert "Input should be 'Beginner', 'Easy', 'Medium', 'Hard' or 'Expert'" in str(
        exc_info.value
    )


def test_question_replace_schema(
    test_model_subject, test_model_topic, test_model_subtopic, test_model_concept
):
    question_data = {
        "text": "What is the capital of France?",
        "difficulty": DifficultyLevel.EASY,
        "subject_ids": [test_model_subject.id],
        "topic_ids": [test_model_topic.id],
        "subtopic_ids": [test_model_subtopic.id],
        "concept_ids": [test_model_concept.id],
        "answer_choice_ids": [1, 2],
        "question_tag_ids": [1, 2],
        "question_set_ids": [1],
    }
    question_schema = QuestionReplaceSchema(**question_data)
    assert question_schema.text == "What is the capital of France?"
    assert question_schema.difficulty == DifficultyLevel.EASY
    assert question_schema.subject_ids == [test_model_subject.id]
    assert question_schema.topic_ids == [test_model_topic.id]
    assert question_schema.subtopic_ids == [test_model_subtopic.id]
    assert question_schema.concept_ids == [test_model_concept.id]
    assert question_schema.answer_choice_ids == [1, 2]
    assert question_schema.question_tag_ids == [1, 2]
    assert question_schema.question_set_ids == [1]


def test_question_replace_schema_validation():
    with pytest.raises(ValidationError) as exc_info:
        QuestionReplaceSchema(text="", difficulty=DifficultyLevel.EASY)
    assert "String should have at least 1 character" in str(exc_info.value)


def test_question_update_schema():
    update_data = {
        "text": "Updated question text",
        "difficulty": DifficultyLevel.MEDIUM,
        "subject_ids": [1],
        "answer_choice_ids": [3, 4],
    }
    update_schema = QuestionUpdateSchema(**update_data)
    assert update_schema.text == "Updated question text"
    assert update_schema.difficulty == DifficultyLevel.MEDIUM
    assert update_schema.subject_ids == [1]
    assert update_schema.answer_choice_ids == [3, 4]


def test_question_with_answers_create_schema(
    test_model_subject, test_model_topic, test_model_subtopic, test_model_concept
):
    question_data = {
        "text": "What is the capital of France?",
        "difficulty": DifficultyLevel.EASY,
        "subject_ids": [test_model_subject.id],
        "topic_ids": [test_model_topic.id],
        "subtopic_ids": [test_model_subtopic.id],
        "concept_ids": [test_model_concept.id],
        "answer_choices": [
            {
                "text": "Paris",
                "is_correct": True,
                "explanation": "Paris is the capital of France",
            },
            {
                "text": "London",
                "is_correct": False,
                "explanation": "London is the capital of the UK",
            },
        ],
    }
    question_schema = QuestionWithAnswersCreateSchema(**question_data)
    assert question_schema.text == "What is the capital of France?"
    assert question_schema.difficulty == DifficultyLevel.EASY
    assert len(question_schema.answer_choices) == 2
    assert question_schema.answer_choices[0].text == "Paris"
    assert question_schema.answer_choices[0].is_correct is True


# pylint: disable=unsubscriptable-object
def test_question_with_answers_replace_schema(
    test_model_subject, test_model_topic, test_model_subtopic, test_model_concept
):
    question_data = {
        "text": "What is the capital of France?",
        "difficulty": DifficultyLevel.EASY,
        "subject_ids": [test_model_subject.id],
        "topic_ids": [test_model_topic.id],
        "subtopic_ids": [test_model_subtopic.id],
        "concept_ids": [test_model_concept.id],
        "answer_choice_ids": [1],  # Existing answer choice
        "new_answer_choices": [
            {
                "text": "London",
                "is_correct": False,
                "explanation": "London is the capital of the UK",
            },
        ],
        "question_tag_ids": [1, 2],
        "question_set_ids": [1],
    }
    question_schema = QuestionWithAnswersReplaceSchema(**question_data)
    assert question_schema.text == "What is the capital of France?"
    assert question_schema.difficulty == DifficultyLevel.EASY
    assert question_schema.answer_choice_ids == [1]
    assert len(question_schema.new_answer_choices) == 1
    assert question_schema.new_answer_choices[0].text == "London"
    assert question_schema.new_answer_choices[0].is_correct is False
    assert question_schema.question_tag_ids == [1, 2]
    assert question_schema.question_set_ids == [1]


def test_detailed_question_schema(
    test_model_subject, test_model_topic, test_model_subtopic, test_model_concept
):
    question_data = {
        "id": 1,
        "text": "What is the capital of France?",
        "difficulty": DifficultyLevel.EASY,
        "subjects": [{"id": test_model_subject.id, "name": test_model_subject.name}],
        "topics": [{"id": test_model_topic.id, "name": test_model_topic.name}],
        "subtopics": [{"id": test_model_subtopic.id, "name": test_model_subtopic.name}],
        "concepts": [{"id": test_model_concept.id, "name": test_model_concept.name}],
        "answer_choices": [
            AnswerChoiceSchema(
                id=1,
                text="Paris",
                is_correct=True,
                explanation="Paris is the capital of France",
            ),
            AnswerChoiceSchema(
                id=2,
                text="London",
                is_correct=False,
                explanation="London is the capital of the UK",
            ),
        ],
        "question_tags": [
            {"id": 1, "name": "geography"},
            {"id": 2, "name": "capitals"},
        ],
        "question_sets": [{"id": 1, "name": "European Capitals"}],
    }
    detailed_schema = DetailedQuestionSchema(**question_data)
    assert detailed_schema.id == 1
    assert detailed_schema.text == "What is the capital of France?"
    assert detailed_schema.difficulty == DifficultyLevel.EASY
    assert detailed_schema.subjects[0]["name"] == test_model_subject.name
    assert detailed_schema.topics[0]["name"] == test_model_topic.name
    assert detailed_schema.subtopics[0]["name"] == test_model_subtopic.name
    assert detailed_schema.concepts[0]["name"] == test_model_concept.name
    assert len(detailed_schema.answer_choices) == 2
    assert len(detailed_schema.question_tags) == 2
    assert detailed_schema.question_tags[0]["name"] == "geography"
    assert detailed_schema.question_tags[1]["name"] == "capitals"
    assert len(detailed_schema.question_sets) == 1
    assert detailed_schema.question_sets[0]["name"] == "European Capitals"


def test_detailed_question_schema_with_object_input(
    test_model_subject, test_model_topic, test_model_subtopic, test_model_concept
):
    question_data = {
        "id": 1,
        "text": "What is the capital of France?",
        "difficulty": DifficultyLevel.EASY,
        "subjects": [{"id": test_model_subject.id, "name": test_model_subject.name}],
        "topics": [{"id": test_model_topic.id, "name": test_model_topic.name}],
        "subtopics": [{"id": test_model_subtopic.id, "name": test_model_subtopic.name}],
        "concepts": [{"id": test_model_concept.id, "name": test_model_concept.name}],
        "answer_choices": [
            AnswerChoiceSchema(
                id=1,
                text="Paris",
                is_correct=True,
                explanation="Paris is the capital of France",
            ),
            AnswerChoiceSchema(
                id=2,
                text="London",
                is_correct=False,
                explanation="London is the capital of the UK",
            ),
        ],
        "question_tags": [
            {"id": 1, "name": "geography"},
            {"id": 2, "name": "capitals"},
        ],
        "question_sets": [{"id": 1, "name": "European Capitals"}],
    }
    detailed_schema = DetailedQuestionSchema(**question_data)
    assert detailed_schema.id == 1
    assert detailed_schema.text == "What is the capital of France?"
    assert detailed_schema.difficulty == DifficultyLevel.EASY
    assert detailed_schema.subjects[0]["name"] == test_model_subject.name
    assert detailed_schema.topics[0]["name"] == test_model_topic.name
    assert detailed_schema.subtopics[0]["name"] == test_model_subtopic.name
    assert detailed_schema.concepts[0]["name"] == test_model_concept.name
    assert len(detailed_schema.answer_choices) == 2
    assert len(detailed_schema.question_tags) == 2
    assert detailed_schema.question_tags[0]["name"] == "geography"
    assert detailed_schema.question_tags[1]["name"] == "capitals"
    assert len(detailed_schema.question_sets) == 1
    assert detailed_schema.question_sets[0]["name"] == "European Capitals"


def test_question_base_schema_empty_text():
    with pytest.raises(ValueError, match="String should have at least 1 character"):
        QuestionBaseSchema(text="", difficulty=DifficultyLevel.EASY)


def test_question_base_schema_whitespace_text():
    with pytest.raises(
        ValueError, match="Question text cannot be empty or only whitespace"
    ):
        QuestionBaseSchema(text="   ", difficulty=DifficultyLevel.EASY)


def test_question_create_schema_empty_text():
    with pytest.raises(ValueError, match="String should have at least 1 character"):
        QuestionCreateSchema(
            text="",
            difficulty=DifficultyLevel.EASY,
            subject_ids=[1],
            topic_ids=[1],
            subtopic_ids=[1],
            concept_ids=[1],
        )


def test_question_update_schema_empty_text():
    with pytest.raises(ValueError, match="String should have at least 1 character"):
        QuestionUpdateSchema(text="")


def test_question_update_schema_whitespace_text():
    with pytest.raises(
        ValueError, match="Question text cannot be empty or only whitespace"
    ):
        QuestionUpdateSchema(text="   ")


def test_question_replace_schema_empty_text():
    with pytest.raises(ValueError, match="String should have at least 1 character"):
        QuestionReplaceSchema(
            text="",
            difficulty=DifficultyLevel.EASY,
            subject_ids=[1],
            topic_ids=[1],
            subtopic_ids=[1],
            concept_ids=[1],
            answer_choice_ids=[1],
            question_tag_ids=[1],
            question_set_ids=[1],
        )


def test_question_replace_schema_whitespace_text():
    with pytest.raises(
        ValueError, match="Question text cannot be empty or only whitespace"
    ):
        QuestionReplaceSchema(
            text="   ",
            difficulty=DifficultyLevel.EASY,
            subject_ids=[1],
            topic_ids=[1],
            subtopic_ids=[1],
            concept_ids=[1],
            answer_choice_ids=[1],
            question_tag_ids=[1],
            question_set_ids=[1],
        )
