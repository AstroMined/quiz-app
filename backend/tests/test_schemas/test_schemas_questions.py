# filename: backend/tests/test_schemas_questions.py

import pytest
from pydantic import ValidationError

from backend.app.schemas.answer_choices import AnswerChoiceSchema
from backend.app.schemas.questions import (DetailedQuestionSchema,
                                           DifficultyLevel,
                                           QuestionCreateSchema,
                                           QuestionUpdateSchema,
                                           QuestionWithAnswersCreateSchema)


def test_question_create_schema(test_model_subject, test_model_topic, test_model_subtopic, test_model_concept):
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
    assert "Input should be 'Beginner', 'Easy', 'Medium', 'Hard' or 'Expert'" in str(exc_info.value)

def test_question_update_schema():
    update_data = {
        "text": "Updated question text",
        "difficulty": DifficultyLevel.MEDIUM,
    }
    update_schema = QuestionUpdateSchema(**update_data)
    assert update_schema.text == "Updated question text"
    assert update_schema.difficulty == DifficultyLevel.MEDIUM

def test_question_with_answers_create_schema(test_model_subject, test_model_topic, test_model_subtopic, test_model_concept):
    question_data = {
        "text": "What is the capital of France?",
        "difficulty": DifficultyLevel.EASY,
        "subject_ids": [test_model_subject.id],
        "topic_ids": [test_model_topic.id],
        "subtopic_ids": [test_model_subtopic.id],
        "concept_ids": [test_model_concept.id],
        "answer_choices": [
            {"text": "Paris", "is_correct": True, "explanation": "Paris is the capital of France"},
            {"text": "London", "is_correct": False, "explanation": "London is the capital of the UK"},
        ]
    }
    question_schema = QuestionWithAnswersCreateSchema(**question_data)
    assert question_schema.text == "What is the capital of France?"
    assert question_schema.difficulty == DifficultyLevel.EASY
    assert len(question_schema.answer_choices) == 2
    assert question_schema.answer_choices[0].text == "Paris"
    assert question_schema.answer_choices[0].is_correct is True

def test_detailed_question_schema(test_model_subject, test_model_topic, test_model_subtopic, test_model_concept):
    question_data = {
        "id": 1,
        "text": "What is the capital of France?",
        "difficulty": DifficultyLevel.EASY,
        "subjects": [{"id": test_model_subject.id, "name": test_model_subject.name}],
        "topics": [{"id": test_model_topic.id, "name": test_model_topic.name}],
        "subtopics": [{"id": test_model_subtopic.id, "name": test_model_subtopic.name}],
        "concepts": [{"id": test_model_concept.id, "name": test_model_concept.name}],
        "answer_choices": [
            AnswerChoiceSchema(id=1, text="Paris", is_correct=True, explanation="Paris is the capital of France"),
            AnswerChoiceSchema(id=2, text="London", is_correct=False, explanation="London is the capital of the UK"),
        ],
        "question_tags": ["geography", "capitals"],
        "question_sets": ["European Capitals"]
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

# You might want to add more tests to cover different input scenarios
def test_detailed_question_schema_with_object_input(test_model_subject, test_model_topic, test_model_subtopic, test_model_concept):
    question_data = {
        "id": 1,
        "text": "What is the capital of France?",
        "difficulty": DifficultyLevel.EASY,
        "subjects": [test_model_subject],
        "topics": [test_model_topic],
        "subtopics": [test_model_subtopic],
        "concepts": [test_model_concept],
        "answer_choices": [
            AnswerChoiceSchema(id=1, text="Paris", is_correct=True, explanation="Paris is the capital of France"),
            AnswerChoiceSchema(id=2, text="London", is_correct=False, explanation="London is the capital of the UK"),
        ],
        "question_tags": ["geography", "capitals"],
        "question_sets": ["European Capitals"]
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

