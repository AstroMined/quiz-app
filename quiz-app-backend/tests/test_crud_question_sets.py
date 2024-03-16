# filename: tests/test_crud_question_sets.py
import pytest
from app.crud import crud_question_sets
from app.schemas import QuestionSetCreate

@pytest.fixture
def question_set_data():
    return QuestionSetCreate(name="Sample Question Set")

def test_create_question_set(db_session, question_set_data):
    """Test creation of a question set."""
    question_set = crud_question_sets.create_question_set(db=db_session, question_set=question_set_data)
    assert question_set is not None, "Question set was not created."
    assert question_set.name == question_set_data.name, "Question set name mismatch."

def test_delete_question_set(db_session, question_set_data):
    """Test deletion of a question set."""
    question_set = crud_question_sets.create_question_set(db=db_session, question_set=question_set_data)
    assert crud_question_sets.delete_question_set(db=db_session, question_set_id=question_set.id) is True, "Question set deletion failed."

# filename: tests/test_crud_question_sets.py

def test_update_question_set_not_found(db_session):
    """
    Test updating a question set that does not exist.
    """
    question_set_id = 999  # Assuming this ID does not exist
    question_set_update = {"name": "Updated Name"}
    updated_question_set = crud_question_sets.update_question_set(db_session, question_set_id, question_set_update)
    assert updated_question_set is None
