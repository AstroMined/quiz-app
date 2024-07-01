# filename: tests/test_crud/test_crud_user_responses.py

from datetime import datetime, timezone
from app.schemas.user_responses import UserResponseCreateSchema, UserResponseUpdateSchema
from app.crud.crud_user_responses import create_user_response_crud, update_user_response_crud, delete_user_response_crud
from app.models.user_responses import UserResponseModel
from app.services.logging_service import logger, sqlalchemy_obj_to_dict

def test_create_and_retrieve_user_response(db_session, test_user_with_group, test_questions):
    response_data = UserResponseCreateSchema(
        db=db_session,
        user_id=test_user_with_group.id,
        question_id=test_questions[0].id,
        answer_choice_id=test_questions[0].answer_choices[0].id
    )
    created_response = create_user_response_crud(db=db_session, user_response=response_data)
    assert created_response is not None, "Failed to create user response."
    assert created_response.user_id == test_user_with_group.id
    assert created_response.question_id == test_questions[0].id
    assert created_response.answer_choice_id == test_questions[0].answer_choices[0].id
    assert created_response.timestamp is not None

def test_update_user_response(db_session, test_user_with_group, test_questions):
    response_data = UserResponseCreateSchema(
        db=db_session,
        user_id=test_user_with_group.id,
        question_id=test_questions[0].id,
        answer_choice_id=test_questions[0].answer_choices[0].id
    )
    created_response = create_user_response_crud(db=db_session, user_response=response_data)
    logger.debug("Created response: %s", sqlalchemy_obj_to_dict(created_response))
    
    update_data = UserResponseUpdateSchema(
        user_id=test_user_with_group.id,
        question_id=test_questions[0].id,
        answer_choice_id=test_questions[0].answer_choices[1].id
    )
    logger.debug("Update data: %s", update_data.model_dump())
    updated_response = update_user_response_crud(db=db_session, user_response_id=created_response.id, user_response=update_data)
    logger.debug("Updated response: %s", sqlalchemy_obj_to_dict(updated_response))
    assert updated_response.answer_choice_id == test_questions[0].answer_choices[1].id
    assert updated_response.timestamp is not None

def test_delete_user_response(db_session, test_user_with_group, test_questions):
    response_data = UserResponseCreateSchema(
        db=db_session,
        user_id=test_user_with_group.id,
        question_id=test_questions[0].id,
        answer_choice_id=test_questions[0].answer_choices[0].id
    )
    created_response = create_user_response_crud(db=db_session, user_response=response_data)
    delete_user_response_crud(db=db_session, user_response_id=created_response.id)
    deleted_response = db_session.query(UserResponseModel).filter(UserResponseModel.id == created_response.id).first()
    assert deleted_response is None
