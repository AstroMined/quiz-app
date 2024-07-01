# filename: tests/test_crud_questions.py

from app.schemas.questions import QuestionCreateSchema, QuestionUpdateSchema, AnswerChoiceCreateSchema
from app.schemas.subjects import SubjectCreateSchema
from app.schemas.topics import TopicCreateSchema
from app.crud.crud_questions import create_question_crud, read_question_crud, update_question_crud, delete_question_crud
from app.crud.crud_topics import create_topic_crud
from app.crud.crud_subjects import create_subject_crud


def test_create_and_retrieve_question(db_session, test_question_set, test_subtopic, test_topic, test_subject):
    """Test creation and retrieval of a question with answer choices."""
    answer_choice_1 = AnswerChoiceCreateSchema(text="Test Answer 1", is_correct=True, explanation="Answer 1 is correct.")
    answer_choice_2 = AnswerChoiceCreateSchema(text="Test Answer 2", is_correct=False, explanation="Answer 2 is incorrect.")
    question_data = QuestionCreateSchema(
        db=db_session,
        text="Sample Question?",
        subject_id=test_subject.id,
        topic_id=test_topic.id,
        subtopic_id=test_subtopic.id,
        difficulty="Easy",
        answer_choices=[answer_choice_1, answer_choice_2],
        question_set_ids=[test_question_set.id]
    )
    created_question = create_question_crud(db=db_session, question=question_data)
    
    assert created_question is not None, "Failed to create question."
    assert created_question.text == "Sample Question?", "Question text does not match."
    assert created_question.difficulty == "Easy", "Question difficulty level does not match."
    assert len(created_question.answer_choices) == 2, "Answer choices not created correctly."
    assert any(choice.text == "Test Answer 1" and choice.explanation == "Answer 1 is correct." for choice in created_question.answer_choices)
    assert any(choice.text == "Test Answer 2" and choice.explanation == "Answer 2 is incorrect." for choice in created_question.answer_choices)
    assert test_question_set.id in created_question.question_set_ids, "Question not associated with the question set."

def test_get_nonexistent_question(db_session):
    """Test retrieval of a non-existent question."""
    question = read_question_crud(db_session, question_id=999)
    assert question is None, "Fetching a non-existent question should return None."

def test_delete_nonexistent_question(db_session):
    """Test deletion of a non-existent question."""
    result = delete_question_crud(db_session, question_id=999)
    assert result is False, "Deleting a non-existent question should return False."

def test_update_question_not_found(db_session):
    """
    Test updating a question that does not exist.
    """
    question_id = 999  # Assuming this ID does not exist
    question_update = {"text": "Updated Question"}
    updated_question = update_question_crud(db_session, question_id, question_update)
    assert updated_question is None

def test_delete_question_not_found(db_session):
    """
    Test deleting a question that does not exist.
    """
    question_id = 999  # Assuming this ID does not exist
    deleted = delete_question_crud(db_session, question_id)
    assert deleted is False

def test_update_question_crud(db_session, test_question, test_question_set):
    """Test updating a question, including its answer choices."""
    question_update = QuestionUpdateSchema(
        text="Updated Question",
        difficulty="Medium",
        answer_choices=[
            {"text": "Updated Answer 1", "is_correct": True, "explanation": "Updated Answer 1 is correct."},
            {"text": "Updated Answer 2", "is_correct": False, "explanation": "Updated Answer 2 is incorrect."},
            {"text": "New Answer 3", "is_correct": False, "explanation": "New Answer 3 is incorrect."}
        ],
        question_set_ids=[test_question_set.id]
    )
    updated_question = update_question_crud(db_session, test_question.id, question_update)

    assert updated_question is not None, "Failed to update question."
    assert updated_question.text == "Updated Question", "Question text not updated correctly."
    assert updated_question.difficulty == "Medium", "Question difficulty not updated correctly."
    assert len(updated_question.answer_choices) == 3, "Answer choices not updated correctly."
    assert any(choice.text == "Updated Answer 1" and choice.explanation == "Updated Answer 1 is correct." for choice in updated_question.answer_choices)
    assert any(choice.text == "Updated Answer 2" and choice.explanation == "Updated Answer 2 is incorrect." for choice in updated_question.answer_choices)
    assert any(choice.text == "New Answer 3" and choice.explanation == "New Answer 3 is incorrect." for choice in updated_question.answer_choices)
    assert test_question_set.id in updated_question.question_set_ids, "Question not associated with the question set after update."
