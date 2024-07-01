# filename: tests/test_crud_question_sets.py

import pytest
from fastapi import HTTPException
from app.crud.crud_question_sets import create_question_set_crud, delete_question_set_crud, update_question_set_crud
from app.crud.crud_subjects import create_subject_crud
from app.schemas.subjects import SubjectCreateSchema
from app.schemas.question_sets import QuestionSetCreateSchema, QuestionSetUpdateSchema


def test_create_question_set_crud(db_session, test_user, test_question, test_group):
    question_set_data = QuestionSetCreateSchema(
        db=db_session,
        name="test_create_question_set_crud Question Set",
        is_public=True,
        creator_id=test_user.id,
        question_ids=[test_question.id],
        group_ids=[test_group.id]
    )
    question_set = create_question_set_crud(db=db_session, question_set=question_set_data)

    assert question_set.name == "test_create_question_set_crud Question Set"
    assert question_set.is_public == True
    assert question_set.creator_id == test_user.id
    assert len(question_set.questions) == 1
    assert question_set.questions[0].id == test_question.id
    assert len(question_set.groups) == 1
    assert question_set.groups[0].id == test_group.id

def test_create_question_set_duplicate_name(db_session, test_user):
    question_set_data = QuestionSetCreateSchema(
        db=db_session,
        name="Duplicate Test Set",
        is_public=True,
        creator_id=test_user.id
    )
    create_question_set_crud(db=db_session, question_set=question_set_data)
    
    with pytest.raises(HTTPException) as exc_info:
        create_question_set_crud(db=db_session, question_set=question_set_data)
    
    assert exc_info.value.status_code == 400
    assert "already exists" in str(exc_info.value.detail)

def test_update_question_set_crud(db_session, test_question_set, test_question, test_group):
    update_data = QuestionSetUpdateSchema(
        db = db_session,
        name="Updated Question Set",
        is_public=False,
        question_ids=[test_question.id],
        group_ids=[test_group.id]
    )
    updated_question_set = update_question_set_crud(db_session, test_question_set.id, update_data)

    assert updated_question_set.name == "Updated Question Set"
    assert updated_question_set.is_public == False
    assert len(updated_question_set.questions) == 1
    assert updated_question_set.questions[0].id == test_question.id
    assert len(updated_question_set.groups) == 1
    assert updated_question_set.groups[0].id == test_group.id

def test_update_question_set_not_found(db_session):
    update_data = QuestionSetUpdateSchema(name="Updated Name")
    with pytest.raises(HTTPException) as exc_info:
        update_question_set_crud(db_session, 999, update_data)
    assert exc_info.value.status_code == 404
    assert "not found" in str(exc_info.value.detail)

def test_delete_question_set(db_session, test_question_set_data, test_user):
    test_question_set_data.name = "Unique Question Set for Deletion"
    question_set_data = QuestionSetCreateSchema(**test_question_set_data.dict())
    question_set = create_question_set_crud(
        db=db_session,
        question_set=question_set_data
    )
    assert delete_question_set_crud(db=db_session, question_set_id=question_set.id) is True, "Question set deletion failed."

def test_delete_question_set_not_found(db_session):
    question_set_id = 999  # Assuming this ID does not exist
    with pytest.raises(HTTPException) as exc_info:
        delete_question_set_crud(db=db_session, question_set_id=question_set_id)
    assert exc_info.value.status_code == 404
    assert f"Question set with ID {question_set_id} not found." in str(exc_info.value.detail)

