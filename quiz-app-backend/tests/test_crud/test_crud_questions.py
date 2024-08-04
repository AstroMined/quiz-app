# filename: tests/test_crud_questions.py

from app.schemas.questions import QuestionCreateSchema, QuestionUpdateSchema, QuestionWithAnswersCreateSchema
from app.schemas.answer_choices import AnswerChoiceCreateSchema
from app.crud.crud_questions import create_question, read_question, update_question, delete_question, create_question_with_answers


def test_create_question_with_answers(db_session, test_subject, test_topic, test_subtopic, test_concept):
    question_data = QuestionWithAnswersCreateSchema(
        text="Test Question",
        subject_id=test_subject.id,
        topic_id=test_topic.id,
        subtopic_id=test_subtopic.id,
        concept_id=test_concept.id,
        difficulty=DifficultyLevel.EASY,
        answer_choices=[
            AnswerChoiceCreateSchema(text="Answer 1", is_correct=True, explanation="Explanation 1"),
            AnswerChoiceCreateSchema(text="Answer 2", is_correct=False, explanation="Explanation 2"),
        ]
    )
    question = create_question_with_answers(db_session, question_data)
    assert question.text == "Test Question"
    assert question.difficulty == "Easy"
    assert len(question.answer_choices) == 2
    assert question.answer_choices[0].text == "Answer 1"
    assert question.answer_choices[1].text == "Answer 2"

def test_read_question_detailed(db_session, test_questions):
    question = read_question(db_session, test_questions[0].id)
    assert question.text == test_questions[0].text
    assert question.difficulty == test_questions[0].difficulty
    assert question.subject == test_questions[0].subject.name
    assert question.topic == test_questions[0].topic.name
    assert question.subtopic == test_questions[0].subtopic.name
    assert question.concept == test_questions[0].concept.name
    assert len(question.answer_choices) == len(test_questions[0].answer_choices)

def test_update_question_with_answer_choices(db_session, test_questions):
    update_data = QuestionUpdateSchema(
        text="Updated Question",
        difficulty=DifficultyLevel.MEDIUM,
        answer_choice_ids=[test_questions[0].answer_choices[0].id]
    )
    updated_question = update_question(db_session, test_questions[0].id, update_data)
    assert updated_question.text == "Updated Question"
    assert updated_question.difficulty == "Medium"
    assert len(updated_question.answer_choices) == 1

def test_get_nonexistent_question(db_session):
    """Test retrieval of a non-existent question."""
    question = read_question(db_session, question_id=999)
    assert question is None, "Fetching a non-existent question should return None."

def test_delete_nonexistent_question(db_session):
    """Test deletion of a non-existent question."""
    result = delete_question(db_session, question_id=999)
    assert result is False, "Deleting a non-existent question should return False."

def test_update_question_not_found(db_session):
    """
    Test updating a question that does not exist.
    """
    question_id = 999  # Assuming this ID does not exist
    question_update = {"text": "Updated Question"}
    updated_question = update_question(db_session, question_id, question_update)
    assert updated_question is None

def test_delete_question_not_found(db_session):
    """
    Test deleting a question that does not exist.
    """
    question_id = 999  # Assuming this ID does not exist
    deleted = delete_question(db_session, question_id)
    assert deleted is False

