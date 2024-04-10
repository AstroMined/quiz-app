# filename: tests/test_crud_question_sets.py

import pytest
from fastapi import HTTPException
from app.crud import (
    create_question_set_crud,
    delete_question_set_crud,
    update_question_set_crud,
    create_subject_crud
)
from app.schemas import QuestionSetUpdateSchema, SubjectCreateSchema, QuestionSetCreateSchema

def test_create_question_set_crud(db_session):
    question_set_data = QuestionSetCreateSchema(name="Test Question Set", is_public=True)
    question_set = create_question_set_crud(db_session, question_set_data)

    assert question_set.name == "Test Question Set"
    assert question_set.is_public == True

def test_delete_question_set(db_session, test_question_set_data):
    test_question_set_data.name = "Unique Question Set for Deletion"
    question_set = create_question_set_crud(db=db_session, question_set=test_question_set_data)
    assert delete_question_set_crud(db=db_session, question_set_id=question_set.id) is True, "Question set deletion failed."

def test_create_question_set_duplicate_name(db_session, test_question_set_data):
    create_question_set_crud(db=db_session, question_set=test_question_set_data)
    with pytest.raises(HTTPException) as exc_info:
        create_question_set_crud(db=db_session, question_set=test_question_set_data)
    assert exc_info.value.status_code == 400
    assert f"Question set with name '{test_question_set_data.name}' already exists." in str(exc_info.value.detail)

def test_update_question_set_not_found(db_session):
    question_set_id = 999
    subject_data = SubjectCreateSchema(name="Test Subject")
    subject = create_subject_crud(db_session, subject_data)
    question_set_update = QuestionSetUpdateSchema(name="Updated Name", subject_id=subject.id)
    with pytest.raises(HTTPException) as exc_info:
        update_question_set_crud(db=db_session, question_set_id=question_set_id, question_set=question_set_update)
    assert exc_info.value.status_code == 404
    assert f"Question set with ID {question_set_id} not found." in str(exc_info.value.detail)

def test_delete_question_set_not_found(db_session):
    question_set_id = 999  # Assuming this ID does not exist
    with pytest.raises(HTTPException) as exc_info:
        delete_question_set_crud(db=db_session, question_set_id=question_set_id)
    assert exc_info.value.status_code == 404
    assert f"Question set with ID {question_set_id} not found." in str(exc_info.value.detail)

def test_update_question_set_crud(db_session, test_question_set, test_question):
    question_set_update = QuestionSetUpdateSchema(name="Updated Question Set", question_ids=[test_question.id])
    updated_question_set = update_question_set_crud(db_session, test_question_set.id, question_set_update)

    assert updated_question_set.name == "Updated Question Set"
    assert test_question.id in updated_question_set.question_ids
