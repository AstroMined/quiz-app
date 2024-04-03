# filename: tests/test_crud_question_sets.py
import pytest
from fastapi import HTTPException
from app.crud import (
    create_question_set,
    delete_question_set,
    update_question_set
)
from app.schemas import QuestionSetCreate, QuestionSetUpdate

@pytest.fixture
def question_set_data():
    return QuestionSetCreate(name="Sample Question Set")

def test_create_question_set(db_session, question_set_data):
    """Test creation of a question set."""
    question_set_data.name = "Unique Question Set"
    question_set = create_question_set(db=db_session, question_set=question_set_data)
    assert question_set is not None, "Question set was not created."
    assert question_set.name == question_set_data.name, "Question set name mismatch."

def test_delete_question_set(db_session, question_set_data):
    """Test deletion of a question set."""
    question_set_data.name = "Unique Question Set for Deletion"
    question_set = create_question_set(db=db_session, question_set=question_set_data)
    assert delete_question_set(db=db_session, question_set_id=question_set.id) is True, "Question set deletion failed."

def test_create_question_set_duplicate_name(db_session, question_set_data):
    create_question_set(db=db_session, question_set=question_set_data)
    with pytest.raises(HTTPException) as exc_info:
        create_question_set(db=db_session, question_set=question_set_data)
    assert exc_info.value.status_code == 400
    assert f"Question set with name '{question_set_data.name}' already exists." in str(exc_info.value.detail)

def test_update_question_set_not_found(db_session):
    question_set_id = 999
    question_set_update = QuestionSetUpdate(name="Updated Name")
    with pytest.raises(HTTPException) as exc_info:
        update_question_set(db=db_session, question_set_id=question_set_id, question_set=question_set_update)
    assert exc_info.value.status_code == 404
    assert f"Question set with ID {question_set_id} not found." in str(exc_info.value.detail)

def test_delete_question_set_not_found(db_session):
    question_set_id = 999  # Assuming this ID does not exist
    with pytest.raises(HTTPException) as exc_info:
        delete_question_set(db=db_session, question_set_id=question_set_id)
    assert exc_info.value.status_code == 404
    assert f"Question set with ID {question_set_id} not found." in str(exc_info.value.detail)
