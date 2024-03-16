# filename: tests/test_crud_questions.py
from app.schemas import QuestionCreate
from app.crud import crud_questions

def test_create_and_retrieve_question(db_session, test_question_set):
    """Test creation and retrieval of a question."""
    question_data = QuestionCreate(text="Sample Question?", subtopic_id=1, question_set_id=test_question_set.id)
    created_question = crud_questions.create_question(db=db_session, question=question_data)
    retrieved_question = crud_questions.get_question(db_session, question_id=created_question.id)
    assert retrieved_question is not None, "Failed to retrieve created question."
    assert retrieved_question.text == "Sample Question?", "Question text does not match."

def test_get_nonexistent_question(db_session):
    """Test retrieval of a non-existent question."""
    question = crud_questions.get_question(db_session, question_id=999)
    assert question is None, "Fetching a non-existent question should return None."

def test_delete_nonexistent_question(db_session):
    """Test deletion of a non-existent question."""
    result = crud_questions.delete_question(db_session, question_id=999)
    assert result is False, "Deleting a non-existent question should return False."

def test_update_question_not_found(db_session):
    """
    Test updating a question that does not exist.
    """
    question_id = 999  # Assuming this ID does not exist
    question_update = {"text": "Updated Question"}
    updated_question = crud_questions.update_question(db_session, question_id, question_update)
    assert updated_question is None

def test_delete_question_not_found(db_session):
    """
    Test deleting a question that does not exist.
    """
    question_id = 999  # Assuming this ID does not exist
    deleted = crud_questions.delete_question(db_session, question_id)
    assert deleted is False
